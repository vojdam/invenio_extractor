# Stažení:
`git clone https://github.com/vojdam/invenio_extractor/`

# Pro vytvoření Docker Image:
`docker build -t invenio_extractor:1.0.0 .`

# Pro spuštění containeru:
`docker run -d -p {cislo_portu}:8080 -v {cesta/k/nio/slozkam}:/invenio_extractor/instance/images --name invenio invenio_extractor:1.0.0`

