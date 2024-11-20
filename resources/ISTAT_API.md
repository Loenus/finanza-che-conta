## ISTAT API

breve descrizione di quel che sono le api di ISTAT, su cui la documentazione documenta poco. 
La mia salvezza è stata questa pagina github che ringrazio.
https://ondata.github.io/guida-api-istat

<br>

### viaggio nei meandri di ISTAT

https://www.istat.it/comunicato-stampa/prezzi-al-consumo-ottobre-2024/
Da qui sono andato a fondo pagina, accedendo alla banca dati.
Nella banca dati sono arrivato qui (Dati>Prezzi>Prezzi al consumo per l'intera comunità (NIC)>dal 2016>Principale"
https://esploradati.istat.it/databrowser/#/it/dw/categories/IT1,Z0400PRI,1.0/PRI_CONWHONAT/DCSP_NIC1B2015/IT1,167_744_DF_DCSP_NIC1B2015_1,1.0
che è dove è indicata la variazione percentuale congiunturale (variazione rispetto al mese esattamente precedente) e la variazione percentuale  tendenziale (variazione rispetto allo stesso mese dell'anno precedente). Quest'ultima solitamente chiamata "inflazione".
spoiler: senza saperlo, in quest ultimo url, avevo già quasi tutti i dati che mi servivano.

seguendo il flusso, ho chiamato questa api che mi ha restituito tutti i tipi di dato che possiede ISTAT fornendomi principalmente id (=structure:Dataflow id), name (Ref id) e description (common:Name):
https://sdmx.istat.it/SDMXWS/rest/dataflow/IT1
Qui, andando un po' a intuito, ho ricavato il name dal link UI della banca data: quindi ho fatto ctrl+F su "DCSP_NIC1B2015", e ho trovato l'id: 167_744

Una volta trovato l'id, volendo scaricarsi tutti i dati (NON FARLO), basterebbe fare: http://sdmx.istat.it/SDMXWS/rest/data/167_744

Per trovare lo schema dati relativo a quell'id, basta fare: http://sdmx.istat.it/SDMXWS/rest/datastructure/IT1/DCSP_NIC1B2015/
Per ogni chiave, posso sapere quali valori può assumere semplicemente facendo una chiamata per tipo.
Ad esempio, se voglio sapere quali valori sono accettabili per un field 
```xml
<Ref id="FREQ" maintainableParentID="CROSS_DOMAIN" maintainableParentVersion="5.3" agencyID="IT1" package="conceptscheme" class="Concept"/>
```
vado a vedere sotto il codelist
```xml
<Ref id="CL_FREQ" version="1.0" agencyID="IT1" package="codelist" class="Codelist"/>
```
e quindi interrogo ISTAT con una chiamata di questo tipo: http://sdmx.istat.it/SDMXWS/rest/codelist/IT1/CL_FREQ (quindi ho messo  agencyID, package e id)
in questo modo mi risponde i tipi accettabili per CL_FREQ e una loro descrizione testuale.

Alcuni dei valori nello schema posso filtrarli nella richiesta. Per sapere quali, faccio la richiesta
http://sdmx.istat.it/SDMXWS/rest/availableconstraint/167_744
e si possono vedere i valori disponibili (senza descrizione però, mentre nella chiamata precedente puntuale per il field, potevo trovarla la descrizione di ogni valore per quel campo)
quindi è possibile filtrare per questi campi nella richiesta dividendoli col punto; esempio /valoreCampo1.valoreCampo2.valoreCampo3/
Se lascio vuoto il valoreCampo allora non viene filtrata la richiesta per quel campo; quindi aggiungere alla richiesta "/..../" equivale a non filtrare (attenzione al numero di puni che è come una virgola tra i campi, quindi deve essere preciso; in questo caso li ho messi a caso perché è un esempio)
Per ogni campo posso specificare più valori con un +; esempio "/.F.082053+072006.."

Sapendo ciò, ho fatto un po'di chiamate tipo https://sdmx.istat.it/SDMXWS/rest/codelist/IT1/CL_TIPO_DATO2 e https://sdmx.istat.it/SDMXWS/rest/codelist/IT1/CL_COICOP_2015 ..

quindi la richiesta GET per ricevere le stesse info ma tramite curl, è questo link: https://sdmx.istat.it/SDMXWS/rest/data/167_744/M.00.IT.6.39/?startPeriod=2023-10-31

<br>


### esaminando la richiesta

https://sdmx.istat.it/SDMXWS/rest/data/167_744/M.00.IT.6+7.39/?startPeriod=2023-10-31

filtro per: [M] Mensilità, Indice Generale (ma ci sono anche le sotto categorie), Italia (invece che regione per regione), 6 (variazione percentuale congiunti; 7 è la tendenziale), 39 è " Indice dei prezzi al consumo per l'intera collettività (base 2015=100) - dati mensili " (ovvero la sotto categoria scelta prima e indicata in alto nell'UI)
