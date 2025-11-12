## Hematology API extract (hemapex)

For research purpose, ICHC team fills databases in REDCAP. One of them focuses on myeloma patients. Myeloma implies a complex care. Typical care trajecory is described below in portuguese. This project aims to automatically extract some of the main elements of care such as treatments or relapses in order to avoid chronophagous manual review.

Textual data was extracted from patients EMR using package registro (developped by ICHC team)

REDCAP database was used as labelled data to evaluate the performances of our method.

This project was developped based on myeloma data. It is somehow specific to this disease context but may be extended to other diseases.
_________

### Myeloma care trajectory

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

## Registro package

For questions about the registro package, contact ICHC Team : registrotmo.ichc@hc.fm.usp.br (Rafael Oliveira, Joaquim Gasparini, Gustavo Acarvalho)
