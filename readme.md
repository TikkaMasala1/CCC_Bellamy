# PDF-hoofdstukken splitsen
Een Python script om PDF-documenten uit te lezen en de inhoud op te splitsen in hoofdstukken op basis van vooraf gedefinieerde regex patronen. Deze tool is ontworpen voor specifieke technische documenten, slaat de eerste pagina's over en gebruikt reguliere expressies om de grenzen van hoofdstukken te bepalen.

## Features
- Slaat een opgegeven aantal beginpagina's over
- Gebruikt document-specifieke regex patronen voor hoofdstuk detectie
- Voert hoofdstukken uit als individuele tekstbestanden
- Ondersteunt meerdere documenttypes met vaste configuraties
## Requirements
- Python 3.6+
- PyMuPDF (fitz): pip installeer pymupdf
## Usage:
```python pdfSplitter.py <path-to-pdf> <instruction-key>```

## Output
Creëert een Output/ directory met submappen vernoemd naar input PDF's:
```
Output/
  ├── document1/
  │ ├── hoofdstuk_1.txt
  │ └── hoofdstuk_2.txt
  └── document2/
      ├── hoofdstuk_1.txt
      └── hoofdstuk_2.txt
```

## (Huidige) ``instruction-key(s)``
- ``CCSK`` - CCSK Study Guide
- ``Zero Trust Planning`` - Zero Trust Planning Study Guide
- ``Zero Trust Strategy`` - Zero Trust Strategy Study Guide
- ``Zero Trust Implementation`` - Zero Trust Implementation Study Guide

## Nieuwe ``instruction-key`` toevoegen
### Stappen
1. Voeg een nieuwe ``instruction-key`` toe aan de dictionary (bijvoorbeeld 'New Security Guide')
2. Bepalen hoeveel begin paginas je moet overslaan.
3. Schrijf een regex patroon dat overeenkomt met hoofdstuktitels in je document
4. Voeg to aan de ``DOCUMENT_INSTRUCTIONS`` dictionary:
```
DOCUMENT_INSTRUCTIONS = {
    # ... existing configurations ...
    
    'New Security Guide': {  # New instruction key
        'skip_pages': 5,     # Skip first 5 pages
        'regex_pattern': r'^Chapter\s+\d+:\s*.+',  # Pattern matching "Chapter X: Title"
        'flags': re.MULTILINE
    }
}
```


