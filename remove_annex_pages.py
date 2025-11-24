"""
Script pour supprimer les pages 21, 22, 23 et 26 des contrats vierges commerciaux.
Ces pages seront remplacées par les annexes pré-remplies générées par ReportLab.
"""
import os
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    from PyPDF2 import PdfReader, PdfWriter

def remove_annex_pages(input_path, output_path):
    """
    Supprime les pages 21, 22, 23 et 26 d'un PDF.
    
    Args:
        input_path: Chemin du PDF source
        output_path: Chemin du PDF de sortie
    """
    # Pages à supprimer (index 0-based)
    pages_to_remove = [20, 21, 22, 25]  # Pages 21, 22, 23, 26 (index - 1)
    
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    total_pages = len(reader.pages)
    print(f"📄 PDF source: {total_pages} pages")
    
    # Ajouter toutes les pages sauf celles à supprimer
    for i in range(total_pages):
        if i not in pages_to_remove:
            writer.add_page(reader.pages[i])
        else:
            print(f"   ❌ Page {i + 1} supprimée")
    
    # Sauvegarder le nouveau PDF
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"✅ PDF modifié: {len(writer.pages)} pages")
    print(f"   Sauvegardé: {output_path}\n")

def main():
    """Traiter tous les contrats vierges dans le dossier contracts/"""
    contracts_dir = os.path.join(os.path.dirname(__file__), 'contracts')
    
    # Liste des fichiers à traiter
    contracts = [
        'NSIA_Convention_Compte_Titres.pdf',
        'GEK --Convention commerciale VF 2025.pdf'
    ]
    
    for contract_file in contracts:
        input_path = os.path.join(contracts_dir, contract_file)
        
        if not os.path.exists(input_path):
            print(f"⚠️  Fichier introuvable: {contract_file}")
            continue
        
        # Créer une sauvegarde
        backup_path = os.path.join(contracts_dir, f"{contract_file}.backup")
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(input_path, backup_path)
            print(f"💾 Sauvegarde créée: {backup_path}")
        
        # Traiter le fichier
        print(f"\n🔧 Traitement: {contract_file}")
        try:
            remove_annex_pages(input_path, input_path)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            # Restaurer depuis la sauvegarde en cas d'erreur
            if os.path.exists(backup_path):
                import shutil
                shutil.copy2(backup_path, input_path)
                print(f"♻️  Restauré depuis la sauvegarde")

if __name__ == '__main__':
    print("=" * 60)
    print("🗑️  SUPPRESSION DES PAGES D'ANNEXES DES CONTRATS VIERGES")
    print("=" * 60)
    print("\nPages à supprimer: 21, 22, 23, 26")
    print("Ces pages seront remplacées par les annexes pré-remplies.\n")
    
    main()
    
    print("\n" + "=" * 60)
    print("✅ TRAITEMENT TERMINÉ")
    print("=" * 60)
    print("\n💡 Les fichiers originaux ont été sauvegardés avec l'extension .backup")
    print("   Si besoin, vous pouvez les restaurer manuellement.\n")
