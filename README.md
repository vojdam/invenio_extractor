# Pro Dockerizaci:
```docker build -t invenio_extractor:1.0.0 .```

# Pro spuštění:
```docker run -d -p 8080:8080 -v {cesta/k/nio/slozkam)}:/invenio_extractor/instance/images --name invenio invenio_extractor:1.0.0```

