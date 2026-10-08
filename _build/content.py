# -*- coding: utf-8 -*-
"""Maison Môa — contenu du site.
Sources : maisonmoa.ch (texte de Charlène), Salonkee (prestations, prix, durées, descriptions),
Facebook / Instagram (publications), flyer « Tarifs & prestations ». Les prix suivent Salonkee
et le flyer d'octobre 2026, qui concordent entre eux."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://welcometothenextlevel.github.io/maisonmoa/'

SITE = dict(
    name='Maison Môa', full='Maison Môa · Institut de beauté',
    phone='078 223 89 09', tel='+41782238909', wa='41782238909',
    email='info@maisonmoa.ch',
    street='Ruelle des Berges 3A', zip='1632', city='Riaz', region='Fribourg',
    access='Entrée par les locaux de Fridogs, 1er étage',
    salonkee='https://salonkee.ch/salon/maison-moa---institut-de-beaute',
    instagram='https://www.instagram.com/maison_moa.beaute.riaz/', ig_handle='@maison_moa.beaute.riaz',
    facebook='https://www.facebook.com/maisonmoariaz',
    maps='https://www.google.com/maps/search/?api=1&query=Maison%20M%C3%B4a%20Institut%20de%20beaut%C3%A9%2C%20Ruelle%20des%20Berges%203A%2C%201632%20Riaz',
    lat=46.640045, lng=7.060975,
    opening='2026-11-02T09:00:00+01:00', opening_txt='lundi 2 novembre 2026',
    corps_des_alpes='https://www.corps-des-alpes.ch/',
)
HOURS = [('Lundi', None), ('Mardi', '9h – 19h'), ('Mercredi', '9h – 19h'), ('Jeudi', '9h – 19h'),
         ('Vendredi', '9h – 19h'), ('Samedi', '8h – 16h'), ('Dimanche', None)]

FIX = [('Préparation des vos ongles', 'Préparation de vos ongles'), ('envlopper', 'envelopper'), ('bouillotes', 'bouillottes'),
       ('choissisez', 'choisissez'), ('Associées à un soin', 'Associés à un soin'), ('afin favoriser', 'afin de favoriser'),
       ('Un soin complet dédié pensé pour', 'Un soin complet pensé pour'), ('précédemment appliquée', 'précédemment appliqué'),
       ('Vos pieds sont délicatement hydratées', 'Vos pieds sont délicatement hydratés'), ('A l\'aide', 'À l\'aide'), ('A vous de choisir', 'À vous de choisir'),
       ('Epilation', 'Épilation'), ('de moins..', 'de moins…'), ('Pour tous types de peaux', 'Pour tous types de peau'),
       ('Convient à tous types de peau', 'Pour tous types de peau'), ('acceuillir', 'accueillir'), ('lumineuse. ', 'lumineuse.'),
       ('3 à 4 semaines sur le poil', '3 à 4 semaines sur le poil.'), ('♡Extraction', '♡ Extraction'), ('♡Modelage', '♡ Modelage')]

def fix(t):
    for a, b in FIX:
        t = t.replace(a, b)
    t = re.sub(r'[ \t]+\n', '\n', t)
    t = re.sub(r'(\S)\n(semaines)', r'\1 \2', t)
    t = t.replace(' ?', ' ?').replace(' :', ' :').replace(' !', ' !')
    return t.strip()

OUTRO_START = ('il ne reste', 'il ne vous reste', 'un petit moment pour soi', 'chaque matin')

def parse_desc(txt):
    """Salonkee description → lead paragraphs, steps (title, detail, options), outro, note."""
    out = dict(lead=[], steps=[], outro='', note='', after=[], skin='')
    if not txt:
        return out
    lines = [l.strip() for l in fix(txt).split('\n')]
    mode, cur = 'lead', None
    for l in lines:
        if not l:
            continue
        low = l.lower().lstrip('♡❀ ')
        if low.startswith('votre rituel en quelques'):
            mode = 'steps'; continue
        if low.startswith('a savoir') or low.startswith('à savoir'):
            mode = 'note'; continue
        if mode == 'note':
            out['note'] = (out['note'] + ' ' + l).strip(); continue
        if low.startswith(OUTRO_START) or (l.startswith('♡') and 'qui vient' in low):
            out['outro'] = l.lstrip('♡ ').strip(); continue
        if l.startswith('♡') or (l.startswith('❀') and (cur is None or not cur['d'].endswith(':'))):
            cur = dict(t=l.lstrip('♡❀ ').strip(), d='', opts=[]); out['steps'].append(cur); mode = 'steps'; continue
        if l.startswith('❀') and cur is not None:
            cur['opts'].append(l.lstrip('❀ ').strip()); continue
        if l.startswith('(') and cur is not None:
            cur['d'] = (cur['d'] + ' ' + l).strip(); continue
        if mode == 'lead' and low.startswith(('pour tous types', 'convient à tous')):
            out['skin'] = l.rstrip('.'); continue
        if mode == 'lead':
            out['lead'].append(l)
        elif cur is not None and not cur['d']:
            cur['d'] = l
        elif cur is not None and cur['d'].endswith(':') and not cur['opts']:
            cur['d'] += ' ' + l
        else:
            out['after'].append(l)
    return out

SK = json.load(open(os.path.join(ROOT, '_src', 'sk_services.json')))

def sk(title, group=None):
    for s in SK:
        if s['title'].strip().lower() == title.lower() and (group is None or s['group'] == group):
            return s
    raise KeyError(title)

def dur(m):
    if m < 60:
        return f'{m} min'
    h, r = divmod(m, 60)
    return f'{h} h' + (f' {r:02d}' if r else '')

def item(title, group, slug, name=None, desc=None, extra=None, dur_override=None, price_prefix='', variants_label=None):
    s = sk(title, group)
    d = parse_desc(desc if desc is not None else s['desc'])
    base = s['items'][0]
    it = dict(id=slug, name=name or fix(s['title']), price=base[0], dur=dur(dur_override or base[1]), minutes=dur_override or base[1],
              prefix=price_prefix, variants=[], **d)
    if len(s['items']) > 1:
        it['variants'] = [(fix(v[2]), v[0], dur(v[1])) for v in s['items']]
        it['variants_label'] = variants_label
    if extra:
        it.update(extra)
    return it

# ---------------------------------------------------------------- soins du visage
G = 'SOINS DU VISAGE'
VISAGE = [
    item('Le Rituel Essentiel', G, 'rituel-essentiel', extra=dict(pick='Quand le temps est compté')),
    item('Le Rituel Harmonie', G, 'rituel-harmonie', extra=dict(pick='Pour rééquilibrer et apaiser')),
    item('Le Rituel Anti-Âge', G, 'rituel-anti-age', extra=dict(pick='Fermeté et éclat')),
    item('Le Rituel Cocooning', G, 'rituel-cocooning', extra=dict(pick='Confort et douceur')),
    item('Le Rituel Ultra Cocooning', G, 'rituel-ultra-cocooning', extra=dict(pick='Le soin le plus enveloppant', signature=True)),
    item('Le Soin Microdermabrasion', G, 'soin-microdermabrasion', extra=dict(pick='Grain de peau et teint uniforme')),
]
VISAGE_PLUS = [
    item('Soin contour des yeux pendant le soin du visage', G, 'contour-des-yeux', name='Soin contour des yeux', extra=dict(addon=True)),
    item('Épilation des sourcils ou de la lèvre pendant le soin du visage', G, 'epilation-pendant-le-soin', name='Épilation des sourcils ou de la lèvre', extra=dict(addon=True)),
]

# ---------------------------------------------------------------- épilations
G = 'ÉPILATION À LA CIRE'
EP_FACE = [('Sourcils', 30, 30), ('Lèvre supérieure', 20, 15), ('Menton', 30, 30), ('Sourcils & lèvre', 40, 30), ('Visage', 50, 45)]
EP_BODY = [('Aisselles', 30, 30), ('Demi-bras', 40, 30), ('Bras entiers', 50, 30), ('Épaules', 35, 30), ('Torse', 60, 30), ('Dos', 60, 30),
           ('Torse & épaules', 70, 30), ('Dos & épaules', 70, 30), ('Bikini simple', 30, 30), ('Bikini échancré', 40, 30),
           ('Bikini intégral', 50, 45), ('Cuisses', 40, 30), ('Demi-jambes', 50, 30), ('Jambes entières', 70, 60)]
EP_FORFAITS = [('Demi-jambes, bikini simple, aisselles', 100, 75), ('Demi-jambes, bikini échancré, aisselles', 110, 75),
               ('Demi-jambes, bikini intégral, aisselles', 120, 90), ('Jambes entières, bikini simple, aisselles', 120, 105),
               ('Jambes entières, bikini échancré, aisselles', 130, 105), ('Jambes entières, bikini intégral, aisselles', 140, 120)]
EP_FORFAIT_PLUS = ('Épilation des sourcils ou de la lèvre dans un forfait', 15, 15)
EP_RITUAL_FINE = parse_desc(sk('Sourcils', G)['desc'])
EP_RITUAL_ROLL = parse_desc(sk('Jambes entières', G)['desc'])

# ---------------------------------------------------------------- regard
G = 'BEAUTÉ DU REGARD'
REGARD = [
    item('Teinture des sourcils', G, 'teinture-sourcils', extra=dict(tip='Des sourcils préalablement démaquillés permettent d’optimiser le résultat de la teinture.')),
    item('Teinture des sourcils avec épilation', G, 'teinture-sourcils-epilation', name='Teinture des sourcils & épilation',
         desc="La coloration sur mesure de vos sourcils, complétée d'une épilation à la cire végane, pour un regard net et intensifié en un seul rendez-vous.\n\nVotre rituel en quelques étapes :\n\n♡ Préparation de la peau et des sourcils\nAvec une solution saline\n\n♡ Teinture\nAprès un échange sur vos envies, je vous accompagne dans le choix de la nuance idéale\n\n♡ Épilation\nUne cire végane sans bandes, hypoallergénique, sans colophane, formulée à basse température\n\nChaque matin, quelques gestes de moins… et un regard toujours aussi soigné ♡"),
    item('Teinture des cils', G, 'teinture-cils', extra=dict(tip='Des cils préalablement démaquillés permettent d’optimiser le résultat de la teinture.')),
    item('Teinture des cils & sourcils', G, 'teinture-cils-sourcils',
         desc="Les deux teintures réunies : des cils plus visibles, des sourcils intensifiés, et un regard qui gagne en profondeur, tout en restant naturel. Résistante à l'eau et au quotidien, la couleur conserve son intensité 3 à 4 semaines sur le poil.\n\nVotre rituel en quelques étapes :\n\n♡ Préparation du regard\nPatchs hydratants sous les yeux et préparation des sourcils\n\n♡ Teinture des sourcils\nUne nuance choisie ensemble, selon vos envies\n\n♡ Teinture des cils\nPour un effet mascara au naturel, même sur les cils les plus clairs\n\nIl ne vous reste plus qu'à ouvrir les yeux… et profiter du résultat ♡"),
]

# ---------------------------------------------------------------- mains
G = 'BEAUTÉ DES MAINS'
MAINS = [
    item('Manucure express', G, 'manucure-express', name='Manucure Express', price_prefix='dès ', variants_label='Avec ou sans dépose'),
    item('Manucure Cocoon', G, 'manucure-cocoon', price_prefix='dès '),
    item('Pose de semi-permanent', G, 'semi-permanent-mains', name='Pose de semi-permanent', price_prefix='dès '),
    item('Manucure Cocoon & semi-permanent', G, 'manucure-cocoon-semi-permanent', price_prefix='dès '),
    item('Dépose de semi-permanent (gel exclus)', G, 'depose-mains', name='Dépose de semi-permanent'),
]

# ---------------------------------------------------------------- pieds
G = 'BEAUTÉ DES PIEDS'
PIEDS = [
    item('Beauté des pieds', G, 'beaute-des-pieds', name='Beauté des pieds Express',
         desc="Un soin net et soigné pour des pieds impeccables, en toute simplicité.\n\nVotre rituel en quelques étapes :\n\n♡ Préparation de vos ongles\nOn prend le temps de révéler la forme naturelle de vos ongles et de soigner délicatement les cuticules pour une finition nette et harmonieuse\n\n♡ La touche finale\nVos pieds sont délicatement hydratés\n\nUn petit moment pour soi, tout simplement ♡"),
    item('Beauté des pieds Cocoon', G, 'beaute-des-pieds-cocoon',
         desc="La version la plus douce, pour des pieds soignés jusque dans le moindre détail.\n\nVotre rituel en quelques étapes :\n\n♡ Préparation de vos ongles\nOn prend le temps de révéler la forme naturelle de vos ongles et de soigner délicatement les cuticules ainsi que vos callosités\n\n♡ Le petit +\nParce que vos pieds méritent de la douceur, choisissez votre gommage cocon :\n❀ Karité, doux et chaleureux\n❀ Jasmin, floral et délicat\n\n♡ La touche finale\nVos pieds sont délicatement hydratés\n\nUn petit moment pour soi, tout simplement ♡"),
    item('Pose de semi-permanent', G, 'semi-permanent-pieds',
         desc="Une couleur nette et brillante qui tient, pour des pieds prêts à se montrer.\n\nVotre rituel en quelques étapes :\n\n♡ Préparation de vos ongles\nOn prend le temps de révéler la forme naturelle de vos ongles et de soigner délicatement les cuticules\n\n♡ La pose de semi-permanent\nChoisissez la teinte qui vous plaît, selon vos envies du moment (tenue : 3 à 4 semaines)"),
    item('Beauté des pieds Cocoon & semi-permanent', G, 'beaute-des-pieds-cocoon-semi-permanent',
         desc=sk('Beauté des pieds Cocoon & semi-permanent', G)['desc'].replace('Parce que vos mains', 'Parce que vos pieds').replace('Le petit plus', 'Le petit +')),
    item('Dépose de semi-permanent (gel exclus)', G, 'depose-pieds', name='Dépose de semi-permanent'),
]

# ---------------------------------------------------------------- corps
G = 'SOINS DU CORPS'
CORPS = [
    item('Gommage du corps', G, 'gommage-du-corps', desc='', extra=dict(
        lead=["Un soin exfoliant au choix, pour retrouver une peau douce, lisse et confortable. Selon vos envies et les besoins de votre peau, choisissez parmi trois gommages aux propriétés complémentaires, et profitez du soin dans la chaleur douce de la table."],
        choices=[('Gommage au sucre, senteurs jasmin', "Composé d'huile de figue de barbarie, pour exfolier, régénérer et hydrater la peau"),
                 ('Gommage au sucre au beurre de karité bio', 'Pour apaiser, nourrir et protéger votre peau'),
                 ('Gommage à sec aux brosses exfoliantes', 'Pour une action redynamisante qui aide à stimuler votre circulation')],
        after=['Quel que soit votre choix, le gommage est délicatement retiré à l’aide de serviettes chaudes, pour une finition confortable et soignée.'],
        outro="Il ne reste plus qu'à retrouver vos vêtements préférés et profiter du résultat ♡")),
    item('Massage du visage, décolleté & cuir chevelu', G, 'massage-visage-decollete', name='Massage du visage, décolleté & cuir chevelu',
         desc="Un moment de détente ciblé avec un massage décontractant du décolleté, du visage et du cuir chevelu. Le soin se termine par un rinçage aux serviettes chaudes et l'application d'une crème adaptée."),
    item('Massage 2 zones au choix', G, 'massage-deux-zones', desc="Un massage sur mesure de 45 minutes, dédié aux deux zones de votre choix, pour relâcher les tensions là où vous en avez besoin."),
    item('Massage des jambes lourdes', G, 'massage-jambes-lourdes', desc="Un massage ciblé des jambes, réalisé avec des manœuvres douces et enveloppantes. Un soin idéal lorsque les jambes sont fatiguées ou semblent lourdes."),
    item('Massage des pieds', G, 'massage-des-pieds', desc="Un soin qui débute par une prise de contact avec des serviettes chaudes, suivie d'un massage relaxant pour délasser vos pieds."),
    item('Soin du dos', G, 'soin-du-dos', desc="Un soin complet du dos : nettoyage, gommage sous vapeur, extraction des comédons et modelage relaxant.", extra=dict(
        steps=[dict(t='Nettoyage', d='Pour préparer la peau du dos', opts=[]), dict(t='Gommage sous vapeur', d='Pour affiner le grain de peau', opts=[]),
               dict(t='Extraction des comédons', d='Pour une peau nette', opts=[]), dict(t='Modelage relaxant', d='Pour dénouer les tensions', opts=[])],
        lead=['Un soin complet du dos, pour une peau nette et un vrai moment de détente.'])),
]

# ---------------------------------------------------------------- univers
SERVICES = [
    dict(slug='soins-du-visage', name='Soins du visage', short='Rituels visage', scene='visage', n='01',
         title='Soins du visage à Riaz, près de Bulle · Maison Môa',
         desc='Six rituels visage à Riaz, près de Bulle : Essentiel, Harmonie, Anti-Âge, Cocooning, Ultra Cocooning et microdermabrasion. Produits naturels, protocoles personnalisés. Dès CHF 85.',
         h1='Soins <em>du visage</em>', eyebrow='Rituels visage',
         intro="Pensés comme de véritables rituels, les soins du visage mêlent produits naturels et sensoriels à des protocoles personnalisés. Du soin express au moment d'exception, chacun prend le temps qu'il faut pour révéler une peau douce, nette et lumineuse.",
         teaser='Des rituels qui mêlent produits naturels et sensoriels à des protocoles personnalisés.',
         img='visage-lumiere', imgs=['visage-modelage-2', 'rituel-bols', 'visage-pinceau'], hover='visage-lumiere', items=VISAGE, plus=VISAGE_PLUS),
    dict(slug='epilations', name='Épilations', short='À la cire végane', scene='epilation', n='02',
         title='Épilation à la cire à Riaz, près de Bulle · Maison Môa',
         desc='Épilation à la cire végane, hypoallergénique et sans colophane à Riaz, près de Bulle : visage, corps et forfaits jambes, bikini, aisselles. Dès CHF 20.',
         h1='Épilations <em>à la cire</em>', eyebrow='Épilations',
         intro="Des produits soigneusement choisis, quelques gestes précis… et il ne reste plus qu'à profiter du résultat. Une cire végane, hypoallergénique et sans colophane, formulée à basse température pour le confort des peaux, même sensibles.",
         teaser='Une cire végane, hypoallergénique et sans colophane, et quelques gestes précis.',
         img='cire-pot', imgs=['cire-pot', 'epilation-jambes', 'corps-des-alpes-lumiere'], hover='cire-pot'),
    dict(slug='beaute-du-regard', name='Beauté du regard', short='Teintures cils & sourcils', scene='regard', n='03',
         title='Teinture cils & sourcils à Riaz, près de Bulle · Maison Môa',
         desc='Teinture des sourcils, des cils, ou les deux, avec ou sans épilation, à Riaz près de Bulle. Une couleur sur mesure qui tient 3 à 4 semaines. Dès CHF 30.',
         h1='Beauté <em>du regard</em>', eyebrow='Rituels regard',
         intro="Pour vous simplifier les matins à venir, même lorsque le réveil sonne un peu trop tôt. Des teintures sur mesure, résistantes à l'eau et au quotidien, qui intensifient votre regard tout en respectant son naturel.",
         teaser='Teintures cils & sourcils, pour des matins plus simples et un regard soigné.',
         img='regard-oeil', imgs=['regard-oeil', 'regard-sourcils', 'regard-cils'], hover='regard-oeil', items=REGARD),
    dict(slug='beaute-des-mains', name='Beauté des mains', short='Manucure & semi-permanent', scene='mains', n='04',
         title='Manucure & semi-permanent à Riaz, près de Bulle · Maison Môa',
         desc='Manucure Express, Manucure Cocoon et pose de semi-permanent à Riaz, près de Bulle. Gommage cocon karité ou jasmin, tenue 3 à 4 semaines. Dès CHF 50.',
         h1='Beauté <em>des mains</em>', eyebrow='Rituels mains',
         intro="Mise en beauté avec le semi-permanent, ou parenthèse plus douce mêlant soin et détente. On prend le temps de révéler la forme naturelle de vos ongles, pour une finition nette et harmonieuse.",
         teaser='Manucure Express ou Cocoon, pose de semi-permanent : des mains nettes et soignées.',
         img='mains-nude', imgs=['mains-limes', 'mains-lin', 'mains-massage'], hover='mains-nude', items=MAINS),
    dict(slug='beaute-des-pieds', name='Beauté des pieds', short='Soin & semi-permanent', scene='pieds', n='05',
         title='Beauté des pieds & semi-permanent à Riaz, près de Bulle · Maison Môa',
         desc='Beauté des pieds Express ou Cocoon, pose de semi-permanent à Riaz, près de Bulle. Soin des ongles, des cuticules et des callosités, gommage cocon. Dès CHF 60.',
         h1='Beauté <em>des pieds</em>', eyebrow='Rituels pieds',
         intro="Une parenthèse douce pour des pieds soignés jusque dans le moindre détail : forme des ongles, cuticules, callosités, gommage cocon et, si vous le souhaitez, une couleur qui tient.",
         teaser='Soin des ongles, gommage cocon et semi-permanent, pour des pieds soignés.',
         img='pieds-massage', imgs=['pieds-huile', 'rituel-bols', 'pieds-massage'], hover='pieds-massage', items=PIEDS),
    dict(slug='soins-du-corps', name='Soins du corps', short='Gommages & massages', scene='corps', n='06',
         title='Soins du corps & massages à Riaz, près de Bulle · Maison Môa',
         desc='Gommage du corps, massages ciblés (visage et cuir chevelu, jambes lourdes, pieds, deux zones au choix) et soin du dos à Riaz, près de Bulle. Dès CHF 70.',
         h1='Soins <em>du corps</em>', eyebrow='Rituels corps',
         intro="Gommages, massages ciblés et soin du dos : des moments pensés pour délasser, dénouer et adoucir, avec les huiles Corps des Alpes, fabriquées à la main dans le canton de Fribourg.",
         teaser='Gommages, massages ciblés et soin du dos, dans la chaleur douce de la table.',
         img='corps-pierres-chaudes', imgs=['corps-massage-dos', 'corps-des-alpes-huiles', 'corps-pierres'], hover='corps-pierres-chaudes', items=CORPS),
]
for s in SERVICES:
    prices = []
    if s['slug'] == 'epilations':
        prices = [p for _, p, _ in EP_FACE + EP_BODY + EP_FORFAITS]
        s['count'] = len(EP_FACE) + len(EP_BODY) + len(EP_FORFAITS)
        s['durs'] = (15, 120)
    else:
        prices = [i['price'] for i in s['items'] if not i['id'].startswith('depose')]
        s['count'] = len(s['items']) + len(s.get('plus', []))
        mins = [i['minutes'] for i in s['items']]
        s['durs'] = (min(mins), max(mins))
    s['from'] = min(prices)

SVC = {s['slug']: s for s in SERVICES}
TOTAL_SOINS = sum(s['count'] for s in SERVICES) + 1

FAQ = [
    ('Où se trouve Maison Môa ?', f"Maison Môa se trouve à la {SITE['street']}, {SITE['zip']} {SITE['city']}, à quelques minutes de Bulle. L'accès se fait par l'entrée des locaux de Fridogs : l'institut est au 1er étage."),
    ('Comment prendre rendez-vous ?', "Le plus simple est de réserver en ligne sur Salonkee, 24 h/24 : vous choisissez votre soin et votre créneau en quelques clics. Vous pouvez aussi appeler le 078 223 89 09, écrire sur WhatsApp ou envoyer une demande depuis la page contact."),
    ('Quand ouvre l’institut ?', "Maison Môa ouvre ses portes le lundi 2 novembre 2026. Les réservations en ligne sont déjà ouvertes, et les premiers rendez-vous sont disponibles dès cette date."),
    ('Quels sont les horaires ?', "Du mardi au vendredi de 9h à 19h, et le samedi de 8h à 16h. Fermé le dimanche et le lundi. Envie d'une parenthèse sur votre pause déjeuner ? Des créneaux sont proposés sur l'heure de midi, selon les disponibilités."),
    ('Où se garer ?', "Des places de parking sont disponibles du côté de l'école primaire de Riaz, à quelques minutes à pied de l'institut. Riaz est aussi desservi par les transports publics et facilement accessible depuis Bulle."),
    ('Quels moyens de paiement sont acceptés ?', "Le paiement se fait par carte bancaire ou en espèces. TWINT n'est pas encore disponible pour le moment."),
    ('Comment annuler ou déplacer un rendez-vous ?', "Merci de prévenir au minimum 24 h à l'avance pour toute annulation ou modification de rendez-vous, par téléphone, WhatsApp ou directement sur Salonkee."),
    ('Puis-je faire déposer un gel posé ailleurs ?', "La dépose se fait uniquement sur un semi-permanent précédemment appliqué chez Maison Môa. Les déposes de gel ou de capsules ne sont pas proposées."),
    ('Le soin microdermabrasion est-il disponible toute l’année ?', "Non : il n'est pas proposé durant la période estivale, en raison de l'exposition solaire accrue et du risque de pigmentation après une exfoliation mécanique. Il est également déconseillé aux peaux très sensibles, réactives ou irritées."),
    ('Proposez-vous des bons cadeaux ?', "Oui. Les bons cadeaux seront bientôt disponibles en ligne ; en attendant, contactez-moi par e-mail ou par téléphone pour préparer votre attention sur mesure, puis venez la retirer directement à l'institut."),
]
