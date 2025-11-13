from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
import logging

from .models import (
    SGI, ClientInvestmentProfile, SGIMatchingRequest,
    ClientSGIInteraction, EmailNotification, AdminDashboardEntry
)
from .models_sgi import SGIAccountTerms, SGIRating, AccountOpeningRequest
from .serializers import (
    SGISerializer, SGIListSerializer, ClientInvestmentProfileSerializer,
    ClientInvestmentProfileCreateSerializer, SGIMatchingRequestSerializer,
    SGIMatchingResultSerializer, ClientSGIInteractionSerializer,
    ClientSGIInteractionCreateSerializer, EmailNotificationSerializer,
    AdminDashboardEntrySerializer, MatchingCriteriaSerializer,
    SGISelectionSerializer, SGIStatisticsSerializer, ClientStatisticsSerializer,
    SGIAccountTermsSerializer, SGIRatingSerializer, SGIRatingCreateSerializer,
    AccountOpeningRequestSerializer, AccountOpeningRequestCreateSerializer
)
from .services import SGIMatchingService, EmailNotificationService
from .services_pdf import ContractPDFService

logger = logging.getLogger(__name__)


class SGIListView(generics.ListAPIView):
    """
    Liste de toutes les SGI actives
    """
    queryset = SGI.objects.filter(is_active=True)
    serializer_class = SGIListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par critères
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        objective = self.request.query_params.get('objective')
        risk_level = self.request.query_params.get('risk_level')
        horizon = self.request.query_params.get('horizon')
        verified_only = self.request.query_params.get('verified_only')
        
        if min_amount:
            queryset = queryset.filter(min_investment_amount__lte=min_amount)
        
        if max_amount:
            queryset = queryset.filter(
                Q(max_investment_amount__gte=max_amount) | 
                Q(max_investment_amount__isnull=True)
            )
        
        # TODO: Réactiver après ajout des champs supported_objectives, supported_risk_levels, supported_horizons
        # if objective:
        #     queryset = queryset.filter(supported_objectives__contains=[objective])
        # 
        # if risk_level:
        #     queryset = queryset.filter(supported_risk_levels__contains=[risk_level])
        # 
        # if horizon:
        #     queryset = queryset.filter(supported_horizons__contains=[horizon])
        
        if verified_only == 'true':
            queryset = queryset.filter(is_verified=True)
        
        return queryset.order_by('-historical_performance', 'management_fees')


class SGIDetailView(generics.RetrieveAPIView):
    """
    Détails d'une SGI spécifique
    """
    queryset = SGI.objects.filter(is_active=True)
    serializer_class = SGISerializer
    permission_classes = [permissions.IsAuthenticated]


class ClientInvestmentProfileView(generics.RetrieveUpdateAPIView):
    """
    Profil d'investissement du client connecté
    """
    serializer_class = ClientInvestmentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = ClientInvestmentProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class ClientInvestmentProfileCreateView(generics.CreateAPIView):
    """
    Création du profil d'investissement client
    """
    serializer_class = ClientInvestmentProfileCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Supprimer l'ancien profil s'il existe
        ClientInvestmentProfile.objects.filter(user=self.request.user).delete()
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def matching_criteria_view(request):
    """
    Retourne les critères de matching disponibles
    """
    criteria = {
        'investment_objectives': SGI.INVESTMENT_OBJECTIVES,
        'risk_levels': SGI.RISK_LEVELS,
        'investment_horizons': SGI.INVESTMENT_HORIZONS,
        'experience_levels': ClientInvestmentProfile.EXPERIENCE_LEVELS
    }
    
    serializer = MatchingCriteriaSerializer(criteria)
    return Response(serializer.data)


class SGIMatchingView(APIView):
    """
    Lancement d'une demande de matching SGI
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Vérifier que le client a un profil complet
            try:
                client_profile = request.user.investment_profile
                if not client_profile.is_complete:
                    return Response(
                        {'error': 'Profil d\'investissement incomplet'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ClientInvestmentProfile.DoesNotExist:
                return Response(
                    {'error': 'Profil d\'investissement non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Créer la demande de matching
            matching_request = SGIMatchingRequest.objects.create(
                client_profile=client_profile,
                status='PROCESSING'
            )
            
            # Lancer le service de matching
            matching_service = SGIMatchingService()
            results = matching_service.find_matching_sgis(client_profile)
            
            # Mettre à jour la demande avec les résultats
            matching_request.matched_sgis = results
            matching_request.total_matches = len([r for r in results if r['matching_score'] >= 50])
            matching_request.status = 'COMPLETED'
            matching_request.completed_at = timezone.now()
            matching_request.save()
            
            # Préparer la réponse
            response_data = {
                'matching_request_id': matching_request.id,
                'total_matches': matching_request.total_matches,
                'matched_sgis': results,
                'has_matches': matching_request.total_matches > 0,
                'fallback_message': None
            }
            
            if matching_request.total_matches == 0:
                response_data['fallback_message'] = (
                    "Aucune SGI ne correspond parfaitement à vos critères. "
                    "Vous pouvez consulter toutes les SGI disponibles pour faire votre choix."
                )
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur lors du matching SGI: {str(e)}")
            
            # Marquer la demande comme échouée si elle existe
            if 'matching_request' in locals():
                matching_request.status = 'FAILED'
                matching_request.save()
            
            return Response(
                {'error': 'Erreur interne lors du matching'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SGIMatchingResultsView(generics.RetrieveAPIView):
    """
    Récupération des résultats d'une demande de matching
    """
    queryset = SGIMatchingRequest.objects.all()
    serializer_class = SGIMatchingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().filter(
            client_profile__user=self.request.user
        )


class SGISelectionView(APIView):
    """
    Sélection d'une SGI par le client
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = SGISelectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Récupérer le profil client
            try:
                client_profile = request.user.investment_profile
            except ClientInvestmentProfile.DoesNotExist:
                return Response(
                    {'error': 'Profil d\'investissement non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Récupérer la SGI
            sgi = get_object_or_404(SGI, id=serializer.validated_data['sgi_id'], is_active=True)
            
            # Créer l'interaction de sélection
            interaction = ClientSGIInteraction.objects.create(
                client_profile=client_profile,
                sgi=sgi,
                interaction_type='SELECTION',
                matching_score=serializer.validated_data['matching_score'],
                notes=serializer.validated_data.get('notes', ''),
                status='INITIATED'
            )
            
            # Créer l'entrée dashboard admin
            AdminDashboardEntry.objects.create(
                client_interaction=interaction
            )
            
            # Envoyer les notifications email
            email_service = EmailNotificationService()
            email_service.send_sgi_selection_notifications(interaction)
            
            # Préparer la réponse
            interaction_serializer = ClientSGIInteractionSerializer(interaction)
            
            return Response({
                'message': 'Sélection SGI enregistrée avec succès',
                'interaction': interaction_serializer.data,
                'next_steps': [
                    'Le manager de la SGI a été notifié de votre intérêt',
                    'Vous recevrez un email de confirmation',
                    'La SGI vous contactera dans les 48h',
                    'Vous pouvez suivre l\'évolution dans votre espace client'
                ]
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sélection SGI: {str(e)}")
            return Response(
                {'error': 'Erreur interne lors de la sélection'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SGIComparatorView(APIView):
    """
    Comparateur et tri des SGI basé sur les conditions d'ouverture et filtres
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = SGI.objects.filter(is_active=True)
        terms = SGIAccountTerms.objects.select_related('sgi').filter(sgi__in=qs)

        # Filtres
        country = request.query_params.get('country')
        bank_name = request.query_params.get('bank')
        sgi_name = request.query_params.get('sgi_name')
        digital_only = request.query_params.get('digital_only')

        if country:
            terms = terms.filter(country__iexact=country)
        if sgi_name:
            terms = terms.filter(sgi__name__icontains=sgi_name)
        if digital_only == 'true':
            terms = terms.filter(is_digital_opening=True)
        if bank_name:
            terms = terms.filter(preferred_customer_banks__icontains=bank_name)

        # Tri
        order_by = request.query_params.get('order_by', 'minimum_amount_value')
        direction = '' if request.query_params.get('order', 'asc') == 'asc' else '-'
        safe_fields = {
            'minimum_amount_value': 'minimum_amount_value',
            'opening_fees_amount': 'opening_fees_amount',
            'custody_fees': 'custody_fees',
        }
        if order_by in safe_fields:
            terms = terms.order_by(f"{direction}{safe_fields[order_by]}")

        data = []
        for t in terms:
            s = t.sgi
            data.append({
                'sgi': SGIListSerializer(s).data,
                'terms': SGIAccountTermsSerializer(t).data,
                'avg_rating': float(SGIRating.objects.filter(sgi=s).aggregate(Avg('score'))['score__avg'] or 0),
                'ratings_count': SGIRating.objects.filter(sgi=s).count(),
            })
        return Response({'results': data, 'total': len(data)})


class ComparatorMatchView(APIView):
    """
    Reçoit les entrées du stepper et renvoie des SGI qui matchent.
    POST /api/sgis/comparator/match/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            payload = request.data or {}
            wants_100_percent_digital_sgi = bool(payload.get('wants_100_percent_digital_sgi'))
            available_minimum_amount = payload.get('available_minimum_amount')
            try:
                from decimal import Decimal
                available_minimum_amount = Decimal(str(available_minimum_amount)) if available_minimum_amount not in (None, '') else None
            except Exception:
                available_minimum_amount = None

            # Méthodes d'alimentation cochées
            funding_flags = {
                'VISA': bool(payload.get('funding_by_visa')),
                'MOBILE_MONEY': bool(payload.get('funding_by_mobile_money')),
                'BANK_TRANSFER': bool(payload.get('funding_by_bank_transfer')),
            }
            # Autres méthodes informatives (intermédiaire/WU...) non filtrantes pour le moment

            # Base SGI actives
            sgi_qs = SGI.objects.filter(is_active=True)
            terms_qs = SGIAccountTerms.objects.select_related('sgi').filter(sgi__in=sgi_qs)

            # Filtre digital si demandé
            if wants_100_percent_digital_sgi:
                terms_qs = terms_qs.filter(is_digital_opening=True)

            # Filtre sur montant dispo vs min_investment_amount (SGI)
            if available_minimum_amount is not None:
                sgi_ids_amount = sgi_qs.filter(min_investment_amount__lte=available_minimum_amount).values_list('id', flat=True)
                terms_qs = terms_qs.filter(sgi_id__in=list(sgi_ids_amount))

            # Filtre sur méthodes de dépôt: doit contenir au moins une méthode cochée
            wanted_methods = [name for name, v in funding_flags.items() if v]
            if wanted_methods:
                # JSONField contains-any workaround: filtrer en Python après fetch limité
                candidates = list(terms_qs)
                filtered = []
                for t in candidates:
                    dm = t.deposit_methods or []
                    if any(m in dm for m in wanted_methods):
                        filtered.append(t)
                terms_qs = filtered
            else:
                terms_qs = list(terms_qs)

            # Aucune correspondance: fallback à toutes les SGI actives
            fallback = False
            if not terms_qs:
                fallback = True
                terms_qs = list(SGIAccountTerms.objects.select_related('sgi').filter(sgi__is_active=True))

            # Tri: qualité vs frais
            prefer_quality = bool(payload.get('prefer_service_quality_over_fees', True))
            if prefer_quality:
                # Tri par vérification SGI puis performance historique desc puis frais de gestion asc
                def sort_key(t):
                    s = t.sgi
                    return (
                        0 if s.is_verified else 1,
                        -(s.historical_performance or 0),
                        (s.management_fees or 0)
                    )
                terms_qs.sort(key=sort_key)
            else:
                # Frais bas: gestion asc, frais ouverture asc, frais de garde asc
                def coalesce(x):
                    return x if x is not None else 0
                def sort_key(t):
                    s = t.sgi
                    return (
                        coalesce(s.management_fees),
                        coalesce(t.opening_fees_amount),
                        coalesce(t.custody_fees)
                    )
                terms_qs.sort(key=sort_key)

            # Construire la réponse
            results = []
            for t in terms_qs:
                s = t.sgi
                results.append({
                    'sgi': SGIListSerializer(s).data,
                    'terms': SGIAccountTermsSerializer(t).data,
                    'avg_rating': float(SGIRating.objects.filter(sgi=s).aggregate(Avg('score'))['score__avg'] or 0),
                    'ratings_count': SGIRating.objects.filter(sgi=s).count(),
                })

            return Response({
                'results': results,
                'total': len(results),
                'fallback': fallback
            })
        except Exception as e:
            logger.error(f"Erreur comparator match: {str(e)}")
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SGICountriesView(APIView):
    """
    Retourne la liste des pays disponibles depuis les termes SGI saisis par les managers
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        countries = (
            SGIAccountTerms.objects.values_list('country', flat=True)
            .distinct().order_by('country')
        )
        return Response({'countries': list(countries)})


class SGIManagerTermsView(APIView):
    """
    Lecture / mise à jour des conditions d'ouverture de compte (Terms) de la SGI du manager connecté
    """
    permission_classes = [permissions.IsAuthenticated]

    def _resolve_manager_sgi(self, user):
        """Retourne l'objet SGI associé au manager connecté.
        Supporte à la fois SGIManagerProfile (models_sgi_manager) et SGIManager (models_sgi).
        """
        # 1) Essayer le profil détaillé
        try:
            from .models_sgi_manager import SGIManagerProfile  # type: ignore
            profile = SGIManagerProfile.objects.get(user=user)
            return profile.sgi
        except Exception:
            pass

        # 2) Essayer le modèle SGIManager (ancien/nouvel autre module)
        try:
            from .models_sgi import SGIManager, SGIManagerAssignment  # type: ignore
            manager = SGIManager.objects.get(user=user)
            # Chercher une assignation PRIMARY en priorité
            primary = (
                SGIManagerAssignment.objects
                .filter(manager=manager, role='PRIMARY', is_active=True)
                .select_related('sgi')
                .first()
            )
            if primary:
                return primary.sgi
            # Sinon, si une seule SGI est gérée, la prendre
            qs = manager.managed_sgis.all()
            if qs.count() == 1:
                return qs.first()
            # Sinon, aucune SGI déterminable
            return None
        except Exception:
            return None

    def get(self, request):
        sgi_obj = self._resolve_manager_sgi(request.user)
        if not sgi_obj:
            return Response({'error': 'Profil manager SGI introuvable ou aucune SGI associée'}, status=status.HTTP_404_NOT_FOUND)

        terms, _ = SGIAccountTerms.objects.get_or_create(sgi=sgi_obj)
        return Response(SGIAccountTermsSerializer(terms).data)

    def put(self, request):
        sgi_obj = self._resolve_manager_sgi(request.user)
        if not sgi_obj:
            return Response({'error': 'Profil manager SGI introuvable ou aucune SGI associée'}, status=status.HTTP_404_NOT_FOUND)

        terms, _ = SGIAccountTerms.objects.get_or_create(sgi=sgi_obj)
        # Support update SGI name alongside terms
        sgi_name = request.data.get('sgi_name')
        if sgi_name:
            sgi_obj.name = sgi_name
            sgi_obj.save(update_fields=['name'])
        serializer = SGIAccountTermsSerializer(instance=terms, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save(sgi=sgi_obj)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        sgi_obj = self._resolve_manager_sgi(request.user)
        if not sgi_obj:
            return Response({'error': 'Profil manager SGI introuvable ou aucune SGI associée'}, status=status.HTTP_404_NOT_FOUND)

        terms, _ = SGIAccountTerms.objects.get_or_create(sgi=sgi_obj)
        # Support update SGI name alongside terms
        sgi_name = request.data.get('sgi_name')
        if sgi_name:
            sgi_obj.name = sgi_name
            sgi_obj.save(update_fields=['name'])
        serializer = SGIAccountTermsSerializer(instance=terms, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(sgi=sgi_obj)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SGIRatingView(APIView):
    """
    Création/mise à jour de la note d'une SGI par le client
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SGIRatingCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            rating = serializer.save()
            return Response(SGIRatingSerializer(rating).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountOpeningRequestCreateView(APIView):
    """
    Création de la demande d'ouverture de compte titre (SGI optionnelle)
    Envoie des emails à la SGI (si fournie), au client et à Xamila
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AccountOpeningRequestCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            req_obj = serializer.save()

            # Emails enrichis (HTML + pièces jointes si disponibles)
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@xamila.com')
            xamila_email = getattr(settings, 'XAMILA_CONTACT_EMAIL', 'contact@xamila.com')

            sgi_name = getattr(req_obj.sgi, 'name', None) if req_obj.sgi else None
            funding_methods = []
            if req_obj.funding_by_visa: funding_methods.append('Carte Visa')
            if req_obj.funding_by_mobile_money: funding_methods.append('Mobile Money')
            if req_obj.funding_by_bank_transfer: funding_methods.append('Virement Bancaire')
            if req_obj.funding_by_intermediary: funding_methods.append('Intermédiaire/Mandataire')
            if req_obj.funding_by_wu_mg_ria: funding_methods.append('WU/MoneyGram/Ria')
            banks = ', '.join(req_obj.customer_banks_current_account or [])
            prefs = f"Digitale: {'Oui' if req_obj.wants_digital_opening else 'Non'} | En personne: {'Oui' if req_obj.wants_in_person_opening else 'Non'}"

            html_body = f"""
                <h2>Confirmation de votre demande d'ouverture de compte titre</h2>
                <p>Bonjour {req_obj.full_name},</p>
                <p>Nous avons bien reçu votre demande. Notre équipe vous recontactera sous 48h.</p>
                <h3>Récapitulatif</h3>
                <ul>
                  <li><strong>SGI choisie:</strong> {sgi_name or 'Non spécifiée'}</li>
                  <li><strong>Nom complet:</strong> {req_obj.full_name}</li>
                  <li><strong>Email:</strong> {req_obj.email}</li>
                  <li><strong>Téléphone:</strong> {req_obj.phone}</li>
                  <li><strong>Pays de résidence:</strong> {req_obj.country_of_residence}</li>
                  <li><strong>Nationalité:</strong> {req_obj.nationality}</li>
                  <li><strong>Montant disponible:</strong> {req_obj.available_minimum_amount or 'N/A'}</li>
                  <li><strong>Méthodes d'alimentation:</strong> {', '.join(funding_methods) or 'N/A'}</li>
                  <li><strong>Banques actuelles:</strong> {banks or 'N/A'}</li>
                  <li><strong>Préférences:</strong> {prefs}</li>
                </ul>
                <p>Merci de votre confiance,</p>
                <p>L'équipe Xamila</p>
            """
            text_body = (
                f"Bonjour {req_obj.full_name},\n\n"
                "Nous avons bien reçu votre demande. Notre équipe vous recontactera sous 48h.\n\n"
                f"SGI: {sgi_name or 'Non spécifiée'}\n"
                f"Nom: {req_obj.full_name}\n"
                f"Email: {req_obj.email}\n"
                f"Téléphone: {req_obj.phone}\n"
                f"Pays de résidence: {req_obj.country_of_residence}\n"
                f"Nationalité: {req_obj.nationality}\n"
                f"Montant disponible: {req_obj.available_minimum_amount or 'N/A'}\n"
                f"Méthodes d'alimentation: {', '.join(funding_methods) or 'N/A'}\n"
                f"Banques actuelles: {banks or 'N/A'}\n"
                f"Préférences: {prefs}\n\n"
                "Merci de votre confiance,\nL'équipe Xamila"
            )

            # Email au client (HTML + texte)
            msg_client = EmailMultiAlternatives(
                subject="Xamila - Confirmation de votre demande d'ouverture de compte titre",
                body=text_body,
                from_email=from_email,
                to=[req_obj.email],
            )
            msg_client.attach_alternative(html_body, "text/html")
            # Joindre les fichiers uploadés si présents et accessibles
            try:
                if req_obj.photo and req_obj.photo.name:
                    with req_obj.photo.open('rb') as f:
                        msg_client.attach(filename='photo_identite' , content=f.read(), mimetype='application/octet-stream')
                if req_obj.id_card_scan and req_obj.id_card_scan.name:
                    with req_obj.id_card_scan.open('rb') as f:
                        msg_client.attach(filename='piece_identite', content=f.read(), mimetype='application/octet-stream')
            except Exception:
                pass
            msg_client.send(fail_silently=True)

            # Notification SGI (si email manager connu)
            if req_obj.sgi:
                manager_email = getattr(req_obj.sgi, 'manager_email', None)
                if manager_email:
                    html_sgi = f"""
                        <h2>Nouvelle demande de mise en relation client</h2>
                        <p><strong>SGI:</strong> {sgi_name}</p>
                        <ul>
                          <li><strong>Client:</strong> {req_obj.full_name} - {req_obj.email} - {req_obj.phone}</li>
                          <li><strong>Pays/Nationalité:</strong> {req_obj.country_of_residence} / {req_obj.nationality}</li>
                          <li><strong>Montant disponible:</strong> {req_obj.available_minimum_amount or 'N/A'}</li>
                          <li><strong>Méthodes d'alimentation:</strong> {', '.join(funding_methods) or 'N/A'}</li>
                          <li><strong>Banques actuelles:</strong> {banks or 'N/A'}</li>
                          <li><strong>Préférences:</strong> {prefs}</li>
                        </ul>
                    """
                    text_sgi = (
                        f"Nouvelle demande - SGI {sgi_name}\n"
                        f"Client: {req_obj.full_name} - {req_obj.email} - {req_obj.phone}\n"
                        f"Pays/Nationalité: {req_obj.country_of_residence} / {req_obj.nationality}\n"
                        f"Montant: {req_obj.available_minimum_amount or 'N/A'}\n"
                        f"Moyens: {', '.join(funding_methods) or 'N/A'}\n"
                        f"Banques: {banks or 'N/A'}\n"
                        f"Préférences: {prefs}\n"
                    )
                    msg_sgi = EmailMultiAlternatives(
                        subject='Xamila - Nouvelle demande de mise en relation client',
                        body=text_sgi,
                        from_email=from_email,
                        to=[manager_email],
                    )
                    msg_sgi.attach_alternative(html_sgi, "text/html")
                    try:
                        if req_obj.photo and req_obj.photo.name:
                            with req_obj.photo.open('rb') as f:
                                msg_sgi.attach(filename='photo_identite', content=f.read(), mimetype='application/octet-stream')
                        if req_obj.id_card_scan and req_obj.id_card_scan.name:
                            with req_obj.id_card_scan.open('rb') as f:
                                msg_sgi.attach(filename='piece_identite', content=f.read(), mimetype='application/octet-stream')
                    except Exception:
                        pass
                    msg_sgi.send(fail_silently=True)

            # Copie Xamila (HTML court)
            msg_xamila = EmailMultiAlternatives(
                subject='Xamila - Nouvelle demande ouverture de compte',
                body=f"Demande #{req_obj.id} par {req_obj.full_name} ({req_obj.email})",
                from_email=from_email,
                to=[xamila_email],
            )
            msg_xamila.attach_alternative(f"<p>Demande <strong>#{req_obj.id}</strong> par <strong>{req_obj.full_name}</strong> ({req_obj.email})</p>", "text/html")
            msg_xamila.send(fail_silently=True)

            return Response(AccountOpeningRequestSerializer(req_obj).data, status=status.HTTP_201_CREATED)
        except (OSError, PermissionError) as e:
            # Retry creation without file fields to avoid 500 on storage permission issues
            data_wo_files = request.data.copy()
            data_wo_files.pop('photo', None)
            data_wo_files.pop('id_card_scan', None)
            serializer2 = AccountOpeningRequestCreateSerializer(data=data_wo_files, context={'request': request})
            if not serializer2.is_valid():
                return Response(serializer2.errors, status=status.HTTP_400_BAD_REQUEST)
            try:
                req_obj = serializer2.save()
                # proceed to emails as usual
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@xamila.com')
                xamila_email = getattr(settings, 'XAMILA_CONTACT_EMAIL', 'contact@xamila.com')
                send_mail(
                    subject='Xamila - Confirmation de votre demande d\'ouverture de compte titre',
                    message=f"Bonjour {req_obj.full_name},\n\nVotre demande a été reçue. Nous vous recontacterons sous 48h.",
                    from_email=from_email,
                    recipient_list=[req_obj.email],
                    fail_silently=True,
                )
                if req_obj.sgi:
                    manager_email = getattr(req_obj.sgi, 'manager_email', None)
                    if manager_email:
                        send_mail(
                            subject='Xamila - Nouvelle demande de mise en relation client',
                            message=(
                                f"Client: {req_obj.full_name} - {req_obj.email} - {req_obj.phone}\n"
                                f"Pays résidence: {req_obj.country_of_residence} - Nationalité: {req_obj.nationality}\n"
                                f"Montant disponible: {req_obj.available_minimum_amount or 'N/A'}\n"
                                f"Préférences: digital={req_obj.wants_digital_opening}, en_personne={req_obj.wants_in_person_opening}\n"
                            ),
                            from_email=from_email,
                            recipient_list=[manager_email],
                            fail_silently=True,
                        )
                send_mail(
                    subject='Xamila - Nouvelle demande ouverture de compte',
                    message=f"Demande #{req_obj.id} par {req_obj.full_name} ({req_obj.email})",
                    from_email=from_email,
                    recipient_list=[xamila_email],
                    fail_silently=True,
                )
                return Response(AccountOpeningRequestSerializer(req_obj).data, status=status.HTTP_201_CREATED)
            except Exception as e2:
                logger.error(f"Erreur création AccountOpeningRequest (retry sans fichiers): {str(e2)}")
                return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Erreur création AccountOpeningRequest: {str(e)}")
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContractPDFGenerateView(APIView):
    """
    Génère un PDF prérempli depuis AccountOpeningRequest + SGI (+ Terms)
    POST body: { account_opening_request_id?: uuid }
    Si non fourni: prend la dernière demande du client.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .models_sgi import AccountOpeningRequest
        aor_id = request.data.get('account_opening_request_id')
        try:
            if aor_id:
                aor = AccountOpeningRequest.objects.get(id=aor_id, customer=request.user)
            else:
                aor = AccountOpeningRequest.objects.filter(customer=request.user).order_by('-created_at').first()
            if not aor:
                return Response({'error': 'Aucune demande trouvée'}, status=status.HTTP_404_NOT_FOUND)

            service = ContractPDFService()
            ctx = service.build_context(aor)
            html = service.render_html(ctx)
            filename = f"contrat_{aor.id}.pdf"
            return service.generate_pdf_response(html, filename)
        except AccountOpeningRequest.DoesNotExist:
            return Response({'error': 'Demande introuvable'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Erreur génération PDF: {str(e)}")
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccountOpeningRequestListView(generics.ListAPIView):
    """
    Liste des demandes d'ouverture de compte du client connecté
    """
    serializer_class = AccountOpeningRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AccountOpeningRequest.objects.filter(customer=self.request.user).order_by('-created_at')


class ContractPrefillView(APIView):
    """
    Préremplissage du contrat après sélection SGI (Mise en relation élaborée)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, sgi_id):
        try:
            sgi = get_object_or_404(SGI, id=sgi_id, is_active=True)
            terms = getattr(sgi, 'account_terms', None)

            # Heuristique de préremplissage
            client_profile = getattr(request.user, 'investment_profile', None)
            suggested_amount = client_profile.investment_amount if client_profile else sgi.min_investment_amount

            # Déterminer une source de financement suggérée
            funding_source = 'BANK_TRANSFER'
            if terms and 'MOBILE_MONEY' in (terms.deposit_methods or []):
                funding_source = 'MOBILE_MONEY'
            elif terms and 'VISA' in (terms.deposit_methods or []):
                funding_source = 'VISA'

            required_docs = [
                'Formulaire d\'ouverture de compte signé',
                'Copie CNI/Passeport',
                'Justificatif de domicile',
                'Justificatif de revenus',
            ]

            payload = {
                'suggested_investment_amount': suggested_amount,
                'suggested_funding_source': funding_source,
                'required_documents': required_docs,
                'sgi': SGIListSerializer(sgi).data,
                'terms': SGIAccountTermsSerializer(terms).data if terms else None,
            }
            serializer = ContractPrefillResponseSerializer(payload)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erreur prefill contrat: {str(e)}")
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContractSubmitOneClickView(APIView):
    """
    Soumission one-click: crée un Contrat et notifie la SGI
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ContractCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            contract = serializer.save()

            # Notifier SGI
            send_mail(
                subject=f"Xamila - Nouveau contrat à valider ({contract.contract_number})",
                message=(
                    f"Client: {contract.customer.full_name} ({contract.customer.email})\n"
                    f"Montant: {contract.investment_amount} - Source: {contract.funding_source}\n"
                ),
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@xamila.com'),
                recipient_list=[contract.sgi.manager_email],
                fail_silently=True,
            )

            return Response(ContractSerializer(contract).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Erreur soumission contrat: {str(e)}")
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class XamilaAuthorizationToggleView(APIView):
    """
    Autorisation client pour que Xamila reçoive les infos de compte une fois ouvert
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Lie l'autorisation à la dernière AccountOpeningRequest du client
        try:
            aor = AccountOpeningRequest.objects.filter(customer=request.user).order_by('-created_at').first()
            if not aor:
                return Response({'error': 'Aucune demande trouvée'}, status=status.HTTP_400_BAD_REQUEST)
            value = request.data.get('authorize', True)
            aor.authorize_xamila_to_receive_account_info = bool(value)
            aor.save(update_fields=['authorize_xamila_to_receive_account_info', 'updated_at'])
            return Response({'authorized': aor.authorize_xamila_to_receive_account_info})
        except Exception as e:
            logger.error(f"Erreur autorisation Xamila+: {str(e)}")
            return Response({'error': 'Erreur interne'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientInteractionsView(generics.ListAPIView):
    """
    Liste des interactions du client connecté
    """
    serializer_class = ClientSGIInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            client_profile = self.request.user.investment_profile
            return ClientSGIInteraction.objects.filter(
                client_profile=client_profile
            ).order_by('-created_at')
        except ClientInvestmentProfile.DoesNotExist:
            return ClientSGIInteraction.objects.none()


class AdminDashboardView(generics.ListAPIView):
    """
    Dashboard admin pour le suivi des interactions SGI
    """
    queryset = AdminDashboardEntry.objects.all()
    serializer_class = AdminDashboardEntrySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(follow_up_status=status_filter)
        
        # Filtrage par priorité
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filtrage par assignation
        assigned_filter = self.request.query_params.get('assigned_to_me')
        if assigned_filter == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def sgi_statistics_view(request):
    """
    Statistiques générales des SGI
    """
    stats = {
        'total_sgis': SGI.objects.count(),
        'active_sgis': SGI.objects.filter(is_active=True).count(),
        'verified_sgis': SGI.objects.filter(is_verified=True).count(),
        'total_matching_requests': SGIMatchingRequest.objects.count(),
        'successful_matches': SGIMatchingRequest.objects.filter(
            total_matches__gt=0
        ).count(),
        'total_interactions': ClientSGIInteraction.objects.count(),
        'average_matching_score': ClientSGIInteraction.objects.aggregate(
            avg_score=Avg('matching_score')
        )['avg_score'] or 0
    }
    
    serializer = SGIStatisticsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def client_statistics_view(request):
    """
    Statistiques des clients
    """
    profiles = ClientInvestmentProfile.objects.all()
    
    # Calculs statistiques
    total_clients = profiles.count()
    complete_profiles = profiles.filter(is_complete=True).count()
    
    investment_stats = profiles.aggregate(
        total_amount=Sum('investment_amount'),
        avg_amount=Avg('investment_amount')
    )
    
    # Objectifs les plus populaires
    objective_counts = profiles.values('investment_objective').annotate(
        count=Count('investment_objective')
    ).order_by('-count').first()
    
    risk_counts = profiles.values('risk_tolerance').annotate(
        count=Count('risk_tolerance')
    ).order_by('-count').first()
    
    horizon_counts = profiles.values('investment_horizon').annotate(
        count=Count('investment_horizon')
    ).order_by('-count').first()
    
    stats = {
        'total_clients': total_clients,
        'complete_profiles': complete_profiles,
        'total_investment_amount': investment_stats['total_amount'] or 0,
        'average_investment_amount': investment_stats['avg_amount'] or 0,
        'most_popular_objective': objective_counts['investment_objective'] if objective_counts else None,
        'most_popular_risk_level': risk_counts['risk_tolerance'] if risk_counts else None,
        'most_popular_horizon': horizon_counts['investment_horizon'] if horizon_counts else None
    }
    
    serializer = ClientStatisticsSerializer(stats)
    return Response(serializer.data)


class EmailNotificationListView(generics.ListAPIView):
    """
    Liste des notifications email (admin seulement)
    """
    queryset = EmailNotification.objects.all()
    serializer_class = EmailNotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filtrage par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
