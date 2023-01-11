import streamlit as st
from helpers.config import set_page_config


def anchor_from_question(question):
    return question.replace(' ', '-').lower()


set_page_config(
    page_title="FAQ",
    page_icon="🤨"
)

st.markdown("# FAQ 🤨")

data = [
    {
        'question': "🚦 Kan ik de zoektool al gebruiken voor mijn onderzoek?",
        'answer': """Dat kan zeker, maar de applicatie is nog in ontwikkeling. Dit betekend dat de zoektool er elk 
        moment uit kan liggen, functionaliteit nog kan wijzigen en vaker foutmeldingen zal tonen."""
    },
    {
        'question': "📈 Hoe wordt de score bepaald?",
        'answer': """Als basis van de zoektool wordt ElasticSearch gebruikt. Deze open source technologie is 
        marktleider op het gebied van tekst doorzoeken. De onderliggende score engine heeft het Okapi BM25 algoritme 
        als basis. Kort gezegd bestaat de berekende score uit drie factoren:\\
        \\
        **1. Term frequency (TF)** Hoe vaker een zoekterm voorkomt, hoe relevanter het document. ElasticSearch zoekt 
        naast exacte termen ook naar die termen die dezelfde stam hebben (zoals digitaal vs digitalisering).\\
        **2. Inverse document frequency (IDF)** Hoe meer documenten de zoekterm bevatten, hoe minder 
        relevant de zoekterm.\\
        **3. Field length** Hoe langer het document, hoe minder relevant een enkele match is.\\
        \\
        Samengevat, een document krijgt een hoge score als hij vaak één of meerdere zoektermen bevat, die relatief 
        weinig in andere documenten worden gevonden en dat in zo min mogelijk tekst.\\
        \\
        **Dit betekent dus dat beknopte documenten (zoals veel kamerstukken) vaker een hogere score krijgen dan lange 
        (AR) rapporten!**\\
        \\
        Meer informatie over het score algoritme kan je 
        [hier](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables) 
        vinden (engels). """
    },
    {
        'question': "⚡️ Wat betekenen de impact grafieken?",
        'answer': "Er zijn twee soorten grafieken ter ondersteuning van de resultaten: *Impact score* en *Aantal "
                  "documenten*. Waar de *Aantal documenten* puur de documenten telt, somt de *Impact score* de score "
                  "van de resultaten. Dit betekend dat waar een laag scorend document in de *Aantal documenten* "
                  "grafiek evenveel waarde heeft als het best scorende document, bij de *Impact score* grafiek het "
                  "naar ratio is. Hierdoor geeft het een beter beeld hoeveel impact de zoektermen hadden in die "
                  "specifieke tijdsperiode."
    },
    {
        'question': "🔦 Hoe kan ik gedetaileerder zoeken?",
        'answer': """ElasticSearch gebruikt de *lucene* zoekengine onder de motorkap. Dit geeft de mogelijkheid om je 
        zoektermen strakker te kunnen definiëren. Standaard zoekt ElasticSearch op `OR`, met andere woorden één van 
        de termen moet in het document gevonden worden om als resultaat getoond te worden. Dit gegrag kan je 
        makkelijk aanpassen, hieronder een aantalmogelijkheden.\\
        \\
        1. `elastic +lucene`: de `+` geeft aan dat het volgende woord in de zoekresultaten *moet* voorkomen.\\
        2. `elastic -lucene`: de `-` geeft aan dat het volgende woord *niet* in de zoekresultaten mag voorkomen\\
        3. `\"elastic lucene\"`: de `\"` geeft aan dat de worden binnen de quotes exact moeten voorkomen 
        en ook in die volgorde.\\
        4. `elastic AND lucene` de `AND` geeft aan dat beide woorden in het document moeten worden gevonden, de 
        volgorde maakt niet uit.\\
        \\
        De volledige lijst met mogelijkheden kan [hier](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html) 
        worden geraadpleegd. """
    },
    {
        'question': "📏 Hoe wordt de *doc lengte* bepaald?",
        'answer': """De *doc lengte* wordt bepaald door het aantal tekens in het document. De verdeling is al volgt:\\
        1. **Heel klein**: tot 1000 tekens (tot ongeveer 0.5 pagina's)\\
        2. **Klein**: van 1001 tot 10.000 tekens (ongeveer 0.5 tot 5 pagina's)\\
        3. **Middel**: van 10.001 tot 100.000 tekens (ongeveer 5 tot 50 pagina's)\\
        4. **Groot**: van 100.001 tot 500.000 tekens (ongeveer 50 tot 250 pagina's)\\
        5. **Heel groot**: vanaf 500.001 tekens (vanaf ongeveer 250 pagina's)"""
    },
    {
        'question': "🤖 Welke data worden van mij verzameld?",
        'answer': """Ter verbetering van de applicatie wordt anonieme data verzameld. Het gaat hier om:\\
        1. Gezochte zoekterm(en)\\
        2. Geopende zoekresultaten ter verbetering van de relevantie\\
        \\
        Deze gegevens zijn alleen geaggregeerd beschikbaar."""
    },
    {
        'question': "💡 Ik heb een goed idee ter verbetering van de zoektool, waar kan ik terecht?",
        'answer': "Je kan een mail sturen naar [b.steup@rekenkamer.nl](mailto:b.steup@rekenkamer.nl), dan help ik je "
                  "vanuit daar verder."
    },
    {
        'question': "🤷 Mijn vraag staat er niet tussen?",
        'answer': "Je kan een mail sturen naar [b.steup@rekenkamer.nl](mailto:b.steup@rekenkamer.nl), dan help ik je "
                  "vanuit daar verder."
    }
]


def table_of_contents_str(items):
    return "\\\n".join(
        map(
            lambda item: f"{item['question'][0]} [{item['question'][2:]}](#{anchor_from_question(item['question'])})",
            items
        )
    )


def echo_questions(items):
    for item in items:
        st.subheader(item['question'], anchor=anchor_from_question(item['question']))
        st.markdown(item['answer'], unsafe_allow_html=True)


st.markdown("<button plausible-event-name='Test' href='https://google.com'>link</button>", unsafe_allow_html=True)
st.markdown(table_of_contents_str(data))
echo_questions(data)
