## Hematology API extract (hemapex)

For research purpose, ICHC team fills databases in [REDCAP](https://project-redcap.org/). This project aims to automatically extract some of the main elements of hematology patients care such as treatments or relapses in order to avoid chronophagous manual review.

Automatic extraction uses API calls to LLM providers such as OpenAI or Google Gemini. We built a framework for retrieving structured output in this project (mainly built upon [Pydantic](https://docs.pydantic.dev/latest/))<br>
The LLM API is given a _prompt instruction_ + a _patient clinical text_ + a _structured output schema_ and generates a _structured JSON_ as output.

Textual data were extracted from patients Electronic Medical Record (EMR) using the package _registro_ (developped by ICHC team). This package mostly scraps EMRs from [Tasy software](https://www.philips.com/a-w/about/news/media-library/20180726-Philips-Tasy-Electronic-Medical-Record-EMR.html) and aims to extend to the different softwares used at ICHC.

The results were assessed with a comparison with a gold standard. The current REDCAP databases were used as a first labelled data source to evaluate the performances of our method. A manueal review of clinical notes would however provide a more robust gold standard.

This project was developped based on hematology data. It is somehow specific to those diseases context ; in particular the structured pydantic Models and the prompt instructions. However, its general methods for extracting structured information based on textual documents may be extended to any fields.
_________

### Myeloma care trajectory

One of the databses focuses on myeloma patients. Myeloma implies a complex care. Typical care trajecory is described below in portuguese.

Tem muitos esquemas de tratamento possíveis.

#### Detalhes :

1. _Indução_ <br>
Objetivo: reduzir a carga tumoral antes do transplante.<br>
Duração: 4–6 ciclos<br>
Esquemas principais são :

- VCd (Bortezomibe + Ciclofosfamida + Dexametasona) ; Esquema mais usado no Brasil (SUS). Eficaz, custo acessível, bem tolerado, bom em insuficiência renal.

- VRd (Bortezomibe + Lenalidomida + Dexametasona) ; Esquema padrão internacional. Alta resposta, mas custo elevado.

- VTD (Bortezomibe + Talidomida + Dexametasona) ; Alternativa viável quando lenalidomida não está disponível.

- Dara-VRd (Daratumumabe + VRd) ; Esquema mais moderno (uso privado), respostas mais profundas.

2. _Transplante Autólogo ou Alogênico_

3. _Consolidação_ <br>
solamente depois do transplante ; é para eliminar doença residual mínimae e nem é sempre obrigatória<br>
2 ciclos de VRd ou VCd

4. _Manutenção_ <br>
Objetivo: Evita recaída e prolonga sobrevida. <br>
Duração: até progressão ou intolerância.

- Talidomida (± Dexa) ; Mais usada no Brasil (SUS)

- Lenalidomida ; Setor privado ou protocolos de pesquisa

- Bortezomibe ; Pacientes de alto risco citogenético

- Ixazomibe (oral) ; Alternativa em casos refratários ou intolerantes

5. _Radioterapia_ (feita de forma independente ; nem é sempre obrigatória)

_____________

### Relapses post Bone Marrow transplants

Identification of relapses post transplant and the associated dates are other key data that are time-consuming to extract from patient records. This extends above myeloma patients.

_____________

### Results

#### Myeloma treatments

The average cost was approximately 0.01$ for extracting the information for one patient.

A first comparison between REDCAP databases and data extracted using APIs has been made. Below are the results : <br>

number of rghc used for final evaluation 224
the two methods disagree on the number of line for 111 cases among the 224 cases evaluated
number of rghc where the following comparisons are evaluated : 113
number of cells where the two methods agree (dates within 1 month or exact treatment correspondance) : 2872
number of comparisons evaluated: 3211
agreement ratio:  89.0 %

Two limits arise from this comparison with REDCAP database :<br>

- text incompleteness

- data in REDCAP is not always up to date

REDCAP data does not seem a gold standard for comparing with our results. Thus, we consider the next step of the project to be a manual review of a sample of the texts given to the API by a doctor to get a proper gold standard.

#### Transplant relapses

Work in progress with the ICHC team
_____________

## Registro package

For questions about the registro package, contact ICHC Team : registrotmo.ichc@hc.fm.usp.br (Rafael Oliveira, Joaquim Gasparini, Gustavo Acarvalho)
