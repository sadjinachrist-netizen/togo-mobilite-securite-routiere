// Rapport Défi 1 — Administration territoriale et mobilité
// Génère Rapport_Mobilite_Securite_Routiere_Togo.pptx (10 slides)

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const OUT = path.join(__dirname, "Rapport_Mobilite_Securite_Routiere_Togo.pptx");
const CAP = (n) => { const p = path.join(__dirname, "captures", n); return fs.existsSync(p) ? p : null; };
const URL = "togo-mobilite-securite-routiere.streamlit.app";

const C = { dark: "0B3D2E", green: "0F6E4E", lime: "4ADE80", gold: "D9A521", red: "C8453B", ink: "14201A",
            muted: "5F6B66", card: "E8F1EC", redl: "FBEAEA", goldl: "FBF3DD", blue: "2F6690", white: "FFFFFF" };
const HF = "Cambria", BF = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "SADJINA Christ";
pres.title = "Mobilité et sécurité routière au Togo — Défi 1";

// ---------------------------------------------------------------- helpers
const title = (s, t, o = {}) => s.addText(t, { x: 0.5, y: 0.3, w: 9, h: 0.68, fontFace: HF, fontSize: 25, bold: true, color: o.color || C.dark, isTextBox: true, margin: 0, valign: "middle" });
const kicker = (s, t, o = {}) => s.addText(t, { x: 0.5, y: 0.96, w: 9, h: 0.34, fontFace: BF, fontSize: 12, italic: true, color: o.color || C.muted, isTextBox: true, margin: 0, valign: "middle" });
const footer = (s, n, dark = false) => s.addText(`Mobilité et sécurité routière au Togo  ·  SADJINA Christ  ·  ${n} / 10`, { x: 0.5, y: 5.22, w: 9, h: 0.25, fontFace: BF, fontSize: 9, color: dark ? "9FB8AC" : C.muted, isTextBox: true, margin: 0, align: "right" });
const card = (s, x, y, w, h, fill = C.card) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, rectRadius: 0.08 });
function stat(s, x, y, w, h, v, l, color = C.dark, fill = C.card, fs = 28) {
  card(s, x, y, w, h, fill);
  s.addText(v, { x: x + 0.14, y: y + 0.08, w: w - 0.28, h: h * 0.5, fontFace: HF, fontSize: fs, bold: true, color, isTextBox: true, margin: 0, valign: "middle" });
  s.addText(l, { x: x + 0.14, y: y + h * 0.56, w: w - 0.28, h: h * 0.42, fontFace: BF, fontSize: 10, color: C.muted, isTextBox: true, margin: 0, valign: "top" });
}
function box(s, x, y, w, h, head, body, fill = C.card, headColor = C.dark, bfs = 10) {
  card(s, x, y, w, h, fill);
  s.addText([{ text: head, options: { bold: true, color: headColor, fontSize: 11.5, breakLine: true } }, { text: body, options: { color: C.ink, fontSize: bfs } }],
    { x: x + 0.14, y: y + 0.07, w: w - 0.28, h: h - 0.14, fontFace: BF, isTextBox: true, margin: 0, valign: "top" });
}
function numbered(s, x, y, w, n, head, body, color = C.green) {
  s.addShape(pres.shapes.OVAL, { x, y: y + 0.02, w: 0.38, h: 0.38, fill: { color }, line: { color, width: 0 } });
  s.addText(String(n), { x, y: y + 0.02, w: 0.38, h: 0.38, fontFace: HF, fontSize: 14, bold: true, color: C.white, isTextBox: true, margin: 0, align: "center", valign: "middle" });
  s.addText([{ text: head, options: { bold: true, color: C.ink, fontSize: 11.5, breakLine: true } }, { text: body, options: { color: C.muted, fontSize: 9.5 } }],
    { x: x + 0.48, y, w: w - 0.48, h: 0.72, fontFace: BF, isTextBox: true, margin: 0, valign: "top" });
}
function image(s, file, x, y, w, h, label) {
  const p = CAP(file);
  if (p) { s.addImage({ path: p, x, y, w, h }); s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: C.white, transparency: 100 }, line: { color: "C9D6CE", width: 0.75 } }); }
  else { card(s, x, y, w, h, "DCE7E0"); s.addText(label, { x, y, w, h, fontFace: BF, fontSize: 12, color: C.muted, italic: true, isTextBox: true, align: "center", valign: "middle" }); }
}
const chartBase = { showLegend: false, catAxisLabelColor: C.ink, valAxisLabelColor: C.muted, valGridLine: { color: "E3E8E5", size: 0.5 }, catGridLine: { style: "none" }, catAxisLabelFontSize: 10, valAxisLabelFontSize: 9, dataLabelColor: C.ink, dataLabelFontSize: 9 };

// ================================================================ 1 · Titre
{
  const s = pres.addSlide(); s.background = { color: C.dark };
  s.addText("DATA CHALLENGE · ADMINISTRATION TERRITORIALE ET MOBILITÉ · DÉFI 1", { x: 0.6, y: 0.48, w: 8.8, h: 0.32, fontFace: BF, fontSize: 11, color: C.lime, bold: true, charSpacing: 2, isTextBox: true, margin: 0 });
  s.addText("Le Togo roule à moto, mais forme des automobilistes", { x: 0.6, y: 0.95, w: 6.3, h: 1.6, fontFace: HF, fontSize: 32, bold: true, color: C.white, isTextBox: true, margin: 0, valign: "middle" });
  s.addText("Mobilité et sécurité routière : immatriculations, permis, accidents, état et tracé du réseau routier, auto-écoles et population, préfecture par préfecture.", { x: 0.6, y: 2.7, w: 6.1, h: 0.85, fontFace: BF, fontSize: 13.5, color: "CFE3D8", isTextBox: true, margin: 0, valign: "top" });
  s.addText([{ text: "Tableau de bord interactif : ", options: { color: "9FB8AC", fontSize: 11.5 } }, { text: URL, options: { color: C.lime, fontSize: 12.5, bold: true, hyperlink: { url: "https://" + URL } } }],
    { x: 0.6, y: 3.65, w: 6.3, h: 0.32, fontFace: BF, isTextBox: true, margin: 0 });
  s.addText([{ text: "SADJINA Christ", options: { bold: true, color: C.white, fontSize: 13.5, breakLine: true } }, { text: "Python · Streamlit · Plotly · 7 pages interactives · octobre 2026", options: { color: "9FB8AC", fontSize: 10.5 } }],
    { x: 0.6, y: 4.35, w: 6, h: 0.62, fontFace: BF, isTextBox: true, margin: 0, valign: "bottom" });
  [["72 %", "des véhicules immatriculés sont des deux-roues"], ["7 507", "accidents et 683 morts en 2022"], ["23 / 39", "préfectures sans auto-école agréée", C.lime]].forEach(([v, l, col], i) => {
    const y = 0.95 + i * 1.25;
    s.addText(v, { x: 6.9, y, w: 2.6, h: 0.65, fontFace: HF, fontSize: 30, bold: true, color: col || C.white, isTextBox: true, margin: 0, align: "right", valign: "middle" });
    s.addText(l, { x: 6.5, y: y + 0.63, w: 3.0, h: 0.42, fontFace: BF, fontSize: 10, color: "9FB8AC", isTextBox: true, margin: 0, align: "right" });
  });
  s.addNotes("Le défi : mesurer l'évolution de la mobilité et de la sécurité routière, et recommander. Le tableau de bord en ligne est le livrable principal ; ce rapport en expose la méthode et les résultats.");
}

// ================================================================ 2 · Démarche
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Démarche : sept sources, un pipeline, sept vues");
  kicker(s, "Chaque étape est reproductible par une seule commande, contrôles de cohérence compris.");
  const steps = [["Auditer", "Huit fichiers bruts, dont un export qui regroupe 13 indicateurs de transport sans colonne de thème — c'est là que se trouvent les accidents. Deux pièges d'étiquetage identifiés (slide 4)."],
    ["Fiabiliser", "Longueurs de route calculées par haversine sur les tracés MULTILINESTRING. Hiérarchie de population reconstruite et validée. Référentiel des 39 préfectures complété."],
    ["Croiser", "État du réseau rattaché aux tracés par numéro de route nationale. Réseau, auto-écoles et accidents rapportés à la population 2022, par région et préfecture."],
    ["Restituer", "Sept pages, filtres territoriaux persistants, carte du réseau colorée par état, exports CSV, page méthodologie et limites."]];
  steps.forEach(([h, b], i) => {
    const x = 0.5 + i * 2.3; card(s, x, 1.4, 2.15, 2.7);
    s.addShape(pres.shapes.OVAL, { x: x + 0.14, y: 1.55, w: 0.4, h: 0.4, fill: { color: C.green }, line: { color: C.green, width: 0 } });
    s.addText(String(i + 1), { x: x + 0.14, y: 1.55, w: 0.4, h: 0.4, fontFace: HF, fontSize: 14, bold: true, color: C.white, isTextBox: true, margin: 0, align: "center", valign: "middle" });
    s.addText(h, { x: x + 0.63, y: 1.55, w: 1.45, h: 0.4, fontFace: BF, fontSize: 13, bold: true, color: C.dark, isTextBox: true, margin: 0, valign: "middle" });
    s.addText(b, { x: x + 0.14, y: 2.05, w: 1.87, h: 1.95, fontFace: BF, fontSize: 9.5, color: C.ink, isTextBox: true, margin: 0, valign: "top" });
  });
  box(s, 0.5, 4.25, 9.0, 0.85, "Les sept sources",
      "Routes classées (799 tronçons géolocalisés, 12/2024) · Auto-écoles (272 points, 01/2025) · État du réseau (87 tronçons, 2020) · "
      + "Immatriculations par type (1990-2022) · Permis par catégorie (2007-2022) · Accidents, morts et blessés (2010-2022) · "
      + "Population RGPH-5 (2022). Contours administratifs : geoBoundaries (OSM, 2017), source externe en licence ouverte.", C.card, C.dark, 9.5);
  footer(s, 2);
  s.addNotes("Le pipeline build_data.py est livré dans l'archive : il reconstruit toutes les tables à partir des fichiers bruts.");
}

// ================================================================ 3 · Six chiffres
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Le diagnostic en six chiffres");
  kicker(s, "Un pays qui se motorise vite, se forme peu, et dont le réseau se dégrade inégalement.");
  const items = [["72,1 %", "des 93 770 véhicules immatriculés en 2022 sont des deux-roues — contre 22 % en 1990", C.dark],
    ["19,7 %", "seulement des permis délivrés sont des permis moto (A) : 4 837 sur 24 598", C.red],
    ["7 507", "accidents en 2022, 683 morts et 9 918 blessés — le plus haut niveau depuis 2012", C.red],
    ["9,1 %", "de létalité, contre 15,2 % en 2010 : on survit mieux, mais les accidents sont deux fois plus nombreux", C.dark],
    ["138 / 272", "auto-écoles non agréées — et 23 préfectures sur 39 n'en comptent aucune qui le soit", C.red],
    ["3 373 km", "de réseau classé, dont 563 km en mauvais état et 450 km en travaux (évaluation 2020)", C.dark]];
  items.forEach(([v, l, col], i) => stat(s, 0.5 + (i % 3) * 3.1, 1.42 + Math.floor(i / 3) * 1.73, 2.9, 1.55, v, l, col, col === C.red ? C.redl : C.card));
  footer(s, 3);
  s.addNotes("Tous les taux sont recalculés à partir des effectifs bruts : la série de taux publiée par la source est mal étiquetée (slide 4).");
}

// ================================================================ 4 · Qualité des données
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Trois constats sur la qualité des données");
  kicker(s, "Identifiés par recoupement, corrigés dans le tableau de bord, et documentés dans la page Méthodologie.");
  box(s, 0.5, 1.4, 4.4, 1.75, "① « Accidents mortels /100 000 hab » compte tous les accidents",
      "La série vaut 92,7 en 2022. Or 7 507 accidents ÷ 8 095 498 habitants × 100 000 = 92,7 — et la vérification tient aussi "
      + "sur 2010 (3 101 ÷ 6,2 M = 50,0). Le véritable taux de mortalité routière est de 8,4 morts pour 100 000 habitants, "
      + "soit onze fois moins que le chiffre publié sous ce nom.", C.goldl, "8A6510", 9.5);
  box(s, 5.1, 1.4, 4.4, 1.75, "② « Parc automobile immatriculé » est un flux, pas un stock",
      "La série décroît plusieurs années (85 748 en 2015, 64 120 en 2016) : elle ne peut décrire un parc cumulé. Ce sont les "
      + "véhicules immatriculés dans l'année. Recoupement exact entre deux fichiers : 93 770 − 67 639 deux-roues = 26 131, "
      + "précisément la valeur publiée pour « 4 roues et plus ».", C.goldl, "8A6510", 9.5);
  box(s, 0.5, 3.3, 4.4, 1.3, "③ La préfecture de Mô est absente des deux jeux géolocalisés",
      "Ni route nationale classée, ni auto-école : 52 448 habitants invisibles dans les données. Elle est réintégrée au "
      + "référentiel avec des valeurs nulles — c'est un résultat, pas une donnée manquante.", C.redl, C.red, 9.5);
  box(s, 5.1, 3.3, 4.4, 1.3, "Ce qui manque vraiment",
      "Aucune donnée d'accident en dessous du niveau national : impossible de savoir où l'on meurt, ni sur quel axe. "
      + "Le croisement accidents × réseau × territoire — le plus utile pour agir — n'est pas réalisable avec les données publiées. "
      + "Rupture de série en 2015, signalée et non corrigée.", C.card, C.dark, 9.5);
  footer(s, 4);
  s.addNotes("Ces trois constats sont le résultat d'un travail de vérification, pas des obstacles : ils changent l'interprétation des chiffres.");
}

// ================================================================ 5 · Parc et permis
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Une motorisation à deux roues, une formation à quatre");
  kicker(s, "Véhicules immatriculés par type et permis délivrés par catégorie — le décalage structurant du sujet.");
  const years = ["1990", "1995", "2000", "2005", "2010", "2014", "2016", "2018", "2020", "2022"];
  const deux = [1513, 13883, 10639, 27791, 38638, 51134, 45341, 43063, 44850, 67639];
  const quatre = [5316, 7953, 9341, 13623, 10740, 17834, 18779, 21283, 23890, 26131];
  s.addChart(pres.charts.BAR, [
    { name: "Deux-roues", labels: years, values: deux },
    { name: "Quatre-roues et plus", labels: years, values: quatre },
  ], { ...chartBase, x: 0.5, y: 1.4, w: 5.5, h: 3.2, barDir: "col", barGrouping: "stacked", chartColors: [C.red, C.green],
    showLegend: true, legendPos: "t", legendFontSize: 10, valAxisTitle: "Véhicules immatriculés dans l'année",
    showValAxisTitle: true, valAxisTitleFontSize: 9, showTitle: true, title: "Immatriculations annuelles par type",
    titleFontSize: 11, titleColor: C.dark });
  box(s, 6.25, 1.4, 3.25, 1.5, "72 % de deux-roues en 2022",
      "contre 22 % en 1990. La motorisation du Togo s'est faite en motos : plus accessibles, plus souples en ville, "
      + "et nettement plus exposées en cas de choc.", C.redl, C.red, 9.5);
  box(s, 6.25, 3.0, 3.25, 1.6, "Mais 14 motos immatriculées par permis A délivré",
      "4 837 permis moto en 2022 contre 16 988 permis voiture. L'effort de 2022 (211 permis A en 2021) montre que la "
      + "capacité existe, mais il n'est pas encore installé dans la durée.", C.goldl, "8A6510", 9.5);
  s.addText("Les séries d'immatriculation comptent les véhicules enregistrés chaque année, non le parc en circulation : ni les sorties de parc ni les véhicules non immatriculés ne sont connus.",
    { x: 0.5, y: 4.72, w: 9, h: 0.3, fontFace: BF, fontSize: 9, italic: true, color: C.muted, isTextBox: true, margin: 0 });
  footer(s, 5);
  s.addNotes("Valeurs réelles issues de la série 1990-2022 ; le graphique montre une année sur deux à quatre pour la lisibilité, la série complète est dans le tableau de bord.");
}

// ================================================================ 6 · Sécurité routière
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Plus d'accidents, mais moins mortels");
  kicker(s, "Accidents, morts et blessés de 2010 à 2022, et létalité (part des accidents qui tuent).");
  const yrs = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"];
  s.addChart([
    { type: pres.charts.BAR, data: [{ name: "Accidents", labels: yrs, values: [3101, 7889, 8155, 5401, 5390, 2851, 5393, 5181, 5814, 5402, 7130, 7392, 7507] }],
      options: { chartColors: ["BFD6CA"], barDir: "col" } },
    { type: pres.charts.LINE, data: [{ name: "Létalité (%)", labels: yrs, values: [15.2, 9.4, 9.2, 11.8, 14.9, 16.6, 9.5, 11.2, 10.2, 10.7, 8.1, 9.2, 9.1] }],
      options: { chartColors: [C.red], lineSize: 3, lineDataSymbolSize: 6, secondaryValAxis: true, secondaryCatAxis: true } },
  ], { ...chartBase, x: 0.5, y: 1.4, w: 5.8, h: 3.3, showLegend: true, legendPos: "t", legendFontSize: 10,
    valAxes: [{ showValAxisTitle: true, valAxisTitle: "Accidents", valAxisLabelFontSize: 9, valGridLine: { color: "E3E8E5", size: 0.5 } },
              { showValAxisTitle: true, valAxisTitle: "Létalité (%)", valAxisLabelFontSize: 9, valAxisMaxVal: 20, valGridLine: { style: "none" } }],
    catAxes: [{ catAxisLabelFontSize: 9 }, { catAxisHidden: true }] });
  stat(s, 6.55, 1.4, 2.95, 1.0, "683", "morts en 2022, soit près de 2 par jour · 9 918 blessés", C.red, C.redl, 26);
  stat(s, 6.55, 2.5, 2.95, 1.0, "8,4", "morts pour 100 000 habitants — et non 92,7 comme publié", C.dark, C.card, 26);
  box(s, 6.55, 3.6, 2.95, 1.1, "Trois lectures",
      "En valeur absolue la situation se dégrade ; rapportée à la population elle est stable ; rapportée aux véhicules "
      + "elle s'améliore. La hausse suit d'abord la croissance du parc.", C.card, C.dark, 9);
  footer(s, 6);
  s.addNotes("La létalité passe de 15,2 % à 9,1 % : les soins d'urgence et l'équipement progressent plus vite que la prévention. 2015 est une rupture de série.");
}

// ================================================================ 7 · Réseau routier
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Un réseau de 3 373 km, inégalement entretenu");
  kicker(s, "Tracés géolocalisés colorés par état réel — page « Réseau routier » du tableau de bord.");
  image(s, "carte_reseau.png", 0.5, 1.35, 5.1, 3.3, "Capture — carte du réseau");
  s.addText("Vert : bon état · Jaune : état moyen · Rouge : mauvais état · Bleu : travaux en cours",
    { x: 0.5, y: 4.7, w: 5.1, h: 0.25, fontFace: BF, fontSize: 9, color: C.muted, isTextBox: true, margin: 0 });
  box(s, 5.85, 1.35, 3.65, 1.5, "Comment l'état a été rattaché aux tracés",
      "L'état est publié par tronçon administratif nommé (87 tronçons), les tracés portent un autre libellé. Les deux ont été "
      + "joints par numéro de route nationale : les 50 RN de la table d'état sont toutes retrouvées, 644 tronçons sur 799 "
      + "reçoivent un état. Chaque tronçon prend l'état dominant de sa RN — approximation assumée.", C.goldl, "8A6510", 9);
  const hdr = { bold: true, color: C.white, fill: { color: C.green }, fontSize: 9 };
  s.addTable([[{ text: "Région", options: hdr }, { text: "Km", options: { ...hdr, align: "right" } }, { text: "% revêtu", options: { ...hdr, align: "right" } }, { text: "m / hab.", options: { ...hdr, align: "right" } }],
    ["Plateaux", { text: "1 011", options: { align: "right" } }, { text: "66 %", options: { align: "right" } }, { text: "0,62", options: { align: "right" } }],
    ["Kara", { text: "735", options: { align: "right" } }, { text: "65 %", options: { align: "right" } }, { text: "0,75", options: { align: "right" } }],
    ["Savanes", { text: "530", options: { align: "right" } }, { text: "47 %", options: { align: "right", color: C.red, bold: true } }, { text: "0,46", options: { align: "right" } }],
    ["Maritime", { text: "474", options: { align: "right" } }, { text: "65 %", options: { align: "right" } }, { text: "0,35", options: { align: "right" } }],
    ["Centrale", { text: "460", options: { align: "right" } }, { text: "74 %", options: { align: "right" } }, { text: "0,58", options: { align: "right" } }],
    ["Grand Lomé", { text: "163", options: { align: "right" } }, { text: "94 %", options: { align: "right" } }, { text: "0,07", options: { align: "right", color: C.red, bold: true } }]],
    { x: 5.85, y: 3.0, w: 3.65, colW: [1.3, 0.8, 0.8, 0.75], fontFace: BF, fontSize: 9, color: C.ink, border: { type: "solid", color: "D5E0DA", pt: 0.5 }, rowH: 0.235, valign: "middle" });
  s.addText("Le réseau classé recense les routes nationales et grandes voiries, pas le maillage urbain local : l'indicateur mesure l'accès au réseau structurant, pertinent pour l'enclavement rural, trompeur pour la congestion urbaine.",
    { x: 5.85, y: 4.68, w: 3.65, h: 0.42, fontFace: BF, fontSize: 8.5, italic: true, color: C.muted, isTextBox: true, margin: 0 });
  footer(s, 7);
  s.addNotes("Les Savanes n'ont que 47 % de réseau revêtu. Mô est la seule préfecture sans aucune route nationale classée recensée.");
}

// ================================================================ 8 · Formation
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Former les conducteurs : l'angle mort du dispositif");
  kicker(s, "272 auto-écoles recensées, dont la moitié hors agrément et quatre sur cinq dans le Grand Lomé.");
  const hdr = { bold: true, color: C.white, fill: { color: C.red }, fontSize: 9 };
  const rows = [[{ text: "Région", options: hdr }, { text: "Auto-écoles", options: { ...hdr, align: "right" } }, { text: "dont agréées", options: { ...hdr, align: "right" } }, { text: "Hab. / école", options: { ...hdr, align: "right" } }]];
  [["Grand Lomé", "213", "103", "10 274"], ["Kara", "14", "7", "70 394"], ["Centrale", "12", "4", "66 294"],
   ["Plateaux", "12", "9", "136 329"], ["Maritime", "11", "5", "122 420"], ["Savanes", "10", "4", "114 352"]]
    .forEach(r => rows.push([r[0], { text: r[1], options: { align: "right" } }, { text: r[2], options: { align: "right" } },
                             { text: r[3], options: { align: "right", bold: r[0] === "Plateaux" || r[0] === "Grand Lomé" } }]));
  s.addTable(rows, { x: 0.5, y: 1.4, w: 4.3, colW: [1.35, 1.05, 1.0, 0.9], fontFace: BF, fontSize: 9.5, color: C.ink,
    border: { type: "solid", color: "EAD3D3", pt: 0.5 }, rowH: 0.27, valign: "middle" });
  box(s, 0.5, 3.4, 4.3, 1.25, "Un rapport de 13 à 1",
      "Un habitant des Plateaux dispose de 136 329 habitants par auto-école, contre 10 274 au Grand Lomé. "
      + "78 % des auto-écoles du pays sont concentrées dans la capitale.", C.redl, C.red, 9.5);
  stat(s, 5.1, 1.4, 2.1, 1.25, "138", "auto-écoles non agréées sur 272 recensées (50,7 %)", C.red, C.redl, 26);
  stat(s, 7.4, 1.4, 2.1, 1.25, "23 / 39", "préfectures sans aucune auto-école agréée", C.red, C.redl, 24);
  box(s, 5.1, 2.85, 4.4, 1.8, "Quinze préfectures n'ont aucune auto-école",
      "Haho (305 096 habitants), Dankpen, Est-Mono, Oti-Sud, Tandjoaré, Kéran, Kpendjal-Ouest, Avé, Moyen-Mono, Kpendjal, "
      + "Doufelgou, Binah, Akébou, Danyi et Mô. Huit autres en ont, mais aucune agréée. Au total, 2 932 492 habitants "
      + "vivent dans une préfecture dépourvue de structure de formation encadrée — au moment où le parc deux-roues explose.", C.card, C.dark, 9.5);
  footer(s, 8);
  s.addNotes("Le croisement avec les permis moto est le cœur du diagnostic : là où la formation est absente ou non encadrée, la conduite s'apprend sans contrôle.");
}

// ================================================================ 9 · Recommandations
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Six recommandations territorialisées");
  kicker(s, "Chacune rattachée à un territoire nommé, un nombre d'habitants et une cible chiffrée.");
  const recs = [["Faire du permis moto la priorité de la formation", "67 639 deux-roues immatriculés pour 4 837 permis A. Cible : porter la part des permis A à 40 % en trois ans, par des sessions décentralisées et un format court pour les conducteurs déjà en circulation.", C.red],
    ["Implanter une auto-école agréée dans les 23 préfectures qui n'en ont aucune", "2 932 492 habitants concernés. Priorité : Haho, Tchamba, Dankpen, Yoto, Est-Mono. Le dispositif d'antennes agréées (47 existantes) évite d'avoir à créer 23 écoles complètes.", C.red],
    ["Régulariser ou fermer les 138 auto-écoles non agréées", "Campagne de mise en conformité avec délai, puis registre public consultable avant inscription. Fermer sans alternative aggraverait le déficit : la régularisation doit précéder la sanction.", C.red],
    ["Concentrer l'entretien sur les routes nationales les plus dégradées", "563 km en mauvais état sur 2 199 évalués. Cible : porter chaque région au-dessus de 60 % de réseau revêtu — les Savanes sont à 47 %.", C.green],
    ["Désenclaver Mô et les préfectures sans réseau structurant", "52 448 habitants dans la seule préfecture sans aucune route nationale classée recensée. Treize préfectures restent sous 0,30 m de route par habitant.", C.green],
    ["Publier des données de sécurité routière localisées", "Localiser les accidents au moins à la préfecture, corriger l'intitulé de la série de taux, documenter la rupture de 2015. Sans cela, aucune politique ne peut être ciblée ni évaluée.", C.green]];
  recs.forEach(([h, b, col], i) => numbered(s, 0.5 + (i % 2) * 4.6, 1.38 + Math.floor(i / 2) * 1.22, 4.4, i + 1, h, b, col));
  footer(s, 9);
  s.addNotes("L'indice de priorité du tableau de bord (40 % accès à la formation, 30 % densité du réseau, 30 % qualité) classe Mô, Akébou, Bas-Mono, Oti-Sud, Moyen-Mono et Est-Mono en tête.");
}

// ================================================================ 10 · Livrable et limites
{
  const s = pres.addSlide(); s.background = { color: C.dark };
  title(s, "Limites, perspectives et livrable", { color: C.white });
  kicker(s, "Ce que ces données ne disent pas encore — et ce que le tableau de bord permet de faire dès maintenant.", { color: "9FB8AC" });
  s.addText("Limites", { x: 0.5, y: 1.4, w: 2.9, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: C.lime, isTextBox: true, margin: 0 });
  const lim = ["Aucune donnée d'accident sous le niveau national : impossible de localiser le risque.",
    "Les immatriculations sont un flux annuel, pas un parc en circulation.",
    "Rupture de série en 2015, signalée et non corrigée.",
    "État du réseau 2020, tracés fin 2024, auto-écoles début 2025, population 2022 : millésimes proches mais distincts.",
    "Contours administratifs 2017 : trois préfectures récentes fusionnées sur la carte."];
  s.addText(lim.map((t, i) => ({ text: t, options: { bullet: { code: "25A0" }, breakLine: i < lim.length - 1, paraSpaceAfter: 5 } })),
    { x: 0.5, y: 1.72, w: 2.9, h: 2.8, fontFace: BF, fontSize: 9.5, color: "DCE9E1", isTextBox: true, margin: 0, valign: "top" });
  s.addText("Perspectives", { x: 3.65, y: 1.4, w: 2.7, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: C.lime, isTextBox: true, margin: 0 });
  const per = ["Géolocaliser les accidents pour croiser risque × état du réseau × trafic.",
    "Mesurer la distance de chaque chef-lieu à l'auto-école agréée la plus proche.",
    "Suivre l'indice de priorité chaque année à partir du même pipeline.",
    "Intégrer le contrôle technique et l'âge du parc, non publiés à ce jour."];
  s.addText(per.map((t, i) => ({ text: t, options: { bullet: { code: "25A0" }, breakLine: i < per.length - 1, paraSpaceAfter: 5 } })),
    { x: 3.65, y: 1.72, w: 2.7, h: 2.8, fontFace: BF, fontSize: 9.5, color: "DCE9E1", isTextBox: true, margin: 0, valign: "top" });
  s.addText("Le tableau de bord", { x: 6.6, y: 1.4, w: 2.9, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: C.lime, isTextBox: true, margin: 0 });
  image(s, "vue.png", 6.6, 1.72, 2.9, 1.6, "Capture — vue d'ensemble");
  s.addText([{ text: "7 pages · filtres territoriaux persistants · carte du réseau par état · exports CSV · méthodologie intégrée", options: { color: "DCE9E1", fontSize: 9.5, breakLine: true } },
    { text: "https://" + URL, options: { color: C.lime, fontSize: 10.5, bold: true, hyperlink: { url: "https://" + URL }, breakLine: true } },
    { text: "Code, données brutes et pipeline dans l'archive jointe.", options: { color: "9FB8AC", fontSize: 9, italic: true } }],
    { x: 6.6, y: 3.42, w: 2.9, h: 1.0, fontFace: BF, isTextBox: true, margin: 0, valign: "top" });
  s.addText("On ne sécurise pas une route qu'on n'a pas cartographiée, ni un conducteur qu'on n'a pas formé.",
    { x: 0.5, y: 4.6, w: 9, h: 0.5, fontFace: HF, fontSize: 16, bold: true, italic: true, color: C.white, isTextBox: true, margin: 0, valign: "middle" });
  footer(s, 10, true);
  s.addNotes("Les limites sont des lacunes de l'open data, retournées en recommandation n°6.");
}

pres.writeFile({ fileName: OUT }).then(() => console.log("OK ->", OUT));
