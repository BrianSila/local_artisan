# Database seed data

`flask db-seed-all` seeds the 47 counties, one representative central/major subcounty for each county, and the service categories. It is safe to rerun; existing county codes, county/name subcounty pairs, and category slugs are left unchanged.

For an existing database that already has counties, run only:

```bash
flask db-seed-subcounties
```

The subcounty list is a practical starting dataset for location selection, not the exhaustive official list of every subcounty. Confirm names and boundaries against authoritative county data before using it as a complete administrative directory.
