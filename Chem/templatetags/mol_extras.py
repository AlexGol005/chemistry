from django import template
from django.utils.safestring import mark_safe
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

register = template.Library()

@register.simple_tag
def render_smiles(smiles, width=300, height=300):
    if not smiles:
        return ""
    
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "Invalid SMILES"

    # Настройка отрисовки SVG
    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()
    
    # mark_safe помечает строку как безопасную, чтобы Django не экранировал теги <svg>
    return mark_safe(svg)
