#!/usr/bin/env python3
"""
Script pour remplacer la méthode _send_admin_email corrompue
"""

import re

def patch_admin_email_method():
    file_path = '/var/www/xamila/xamila_backend/core/services_email.py'
    backup_path = file_path + '.before_patch'
    
    # Nouvelle méthode propre
    new_method = '''    def _send_admin_email(self, aor, to_email: str, contract_pdf: bytes, annexes_pdf: bytes):
        """Envoie l'email a un administrateur"""
        subject = f"[ADMIN] Nouvelle demande - {aor.full_name} - {aor.sgi.name if aor.sgi else 'SGI'}"
        
        html_body = f"""
            <h2 style="color: #d32f2f;">Admin - Nouvelle demande d'ouverture de compte</h2>
            <p><strong>Client:</strong> {aor.full_name}</p>
            <p><strong>SGI:</strong> {aor.sgi.name if aor.sgi else 'Non specifiee'}</p>
            <p><strong>Email:</strong> {aor.email}</p>
            <p><strong>Telephone:</strong> {aor.phone}</p>
            <p><strong>Pays:</strong> {aor.country_of_residence}</p>
            <p><strong>Nationalite:</strong> {aor.nationality}</p>
            <p><strong>Profil investisseur:</strong> {aor.investor_profile or 'N/A'}</p>
            <p><strong>Preferences:</strong></p>
            <ul>
                <li>Ouverture digitale: {'Oui' if aor.wants_digital_opening else 'Non'}</li>
                <li>Ouverture en personne: {'Oui' if aor.wants_in_person_opening else 'Non'}</li>
                <li>Xamila+: {'Oui' if aor.wants_xamila_plus else 'Non'}</li>
            </ul>
            <p><strong>Numero de demande:</strong> {aor.id}</p>
            <p><strong>Date de soumission:</strong> {aor.created_at.strftime('%d/%m/%Y %H:%M')}</p>
            <p>Vous trouverez en pieces jointes le contrat et les annexes completes.</p>
            <p>Administration Xamila</p>
        """
        
        text_body = f"""
[ADMIN] Nouvelle demande d'ouverture de compte

Client: {aor.full_name}
SGI: {aor.sgi.name if aor.sgi else 'Non specifiee'}
Email: {aor.email}
Telephone: {aor.phone}
Pays: {aor.country_of_residence}
Nationalite: {aor.nationality}
Profil: {aor.investor_profile or 'N/A'}

Preferences:
- Ouverture digitale: {'Oui' if aor.wants_digital_opening else 'Non'}
- Ouverture en personne: {'Oui' if aor.wants_in_person_opening else 'Non'}
- Xamila+: {'Oui' if aor.wants_xamila_plus else 'Non'}

Numero de demande: {aor.id}
Date: {aor.created_at.strftime('%d/%m/%Y %H:%M')}

Administration Xamila
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=self.from_email,
            to=[to_email],
        )
        email.attach_alternative(html_body, "text/html")
        
        # Attacher le contrat PDF
        sgi_name = aor.sgi.name.replace(' ', '_') if aor.sgi else 'SGI'
        email.attach(
            filename=f'Contrat_{aor.id}.pdf',
            content=contract_pdf,
            mimetype='application/pdf'
        )
        
        # Attacher les annexes PDF
        email.attach(
            filename=f'Annexes_{aor.id}.pdf',
            content=annexes_pdf,
            mimetype='application/pdf'
        )
        
        # Attacher la photo si disponible
        try:
            if aor.photo and aor.photo.name:
                with aor.photo.open('rb') as f:
                    photo_content = f.read()
                    photo_ext = aor.photo.name.split('.')[-1] if '.' in aor.photo.name else 'jpg'
                    email.attach(
                        filename=f'Photo_{aor.full_name.replace(" ", "_")}.{photo_ext}',
                        content=photo_content,
                        mimetype=f'image/{photo_ext}'
                    )
        except Exception as e:
            logger.warning(f"Impossible d'attacher la photo pour l'admin: {e}")
        
        # Attacher la CNI si disponible
        try:
            if aor.id_card_scan and aor.id_card_scan.name:
                with aor.id_card_scan.open('rb') as f:
                    id_content = f.read()
                    id_ext = aor.id_card_scan.name.split('.')[-1] if '.' in aor.id_card_scan.name else 'pdf'
                    mimetype = 'application/pdf' if id_ext.lower() == 'pdf' else f'image/{id_ext}'
                    email.attach(
                        filename=f'CNI_{aor.full_name.replace(" ", "_")}.{id_ext}',
                        content=id_content,
                        mimetype=mimetype
                    )
        except Exception as e:
            logger.warning(f"Impossible d'attacher la CNI pour l'admin: {e}")
        
        email.send()
'''
    
    print("Lecture du fichier...")
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    except:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    
    print("Sauvegarde...")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Recherche de la méthode _send_admin_email...")
    # Pattern pour trouver la méthode complète
    pattern = r'    def _send_admin_email\(self.*?\n        email\.send\(\)'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print(f"Méthode trouvée à la position {match.start()}")
        # Remplacer
        new_content = content[:match.start()] + new_method + content[match.end():]
        
        print("Écriture du fichier corrigé...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✓ Patch appliqué avec succès")
        return True
    else:
        print("✗ Méthode _send_admin_email non trouvée")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("  Patch de la méthode _send_admin_email")
    print("=" * 60)
    print()
    
    if patch_admin_email_method():
        print()
        print("Vérification...")
        import os
        os.system('cd /var/www/xamila/xamila_backend && python3 manage.py check')
        print()
        print("Redémarrage...")
        os.system('sudo systemctl restart xamila')
        import time
        time.sleep(3)
        print()
        print("Test...")
        os.system('curl -s http://localhost:8000/health/ | python3 -m json.tool')
