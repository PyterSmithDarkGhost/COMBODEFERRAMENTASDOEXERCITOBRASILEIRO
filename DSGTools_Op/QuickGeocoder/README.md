# Quick Geocoder
### QGIS 3 plugin for geocoding using many different API's and GeoPy

![](https://img.shields.io/badge/development--version-0.1-brightgreen.svg) ![](https://img.shields.io/badge/stable--date-not--launched-orange.svg) ![](https://img.shields.io/badge/maintainer-diegobenincasa-blue.svg)
---
This plugin is used to geocode a point layer using many different API's, or reverse-geocode a CSV addresses file (adress splitted into fields or not) to a point layer.

Many services require you to have personal "keys" or "id's". Refer to the documentation of the one you want to use.
As a reference, a Bing Maps API key can be obtained [here - https://www.bingmapsportal.com/](https://www.bingmapsportal.com/).

---

Plugin is based on GeoPy geocoding library - [https://geopy.readthedocs.io/en/stable/](https://geopy.readthedocs.io/en/stable/).

---
## USAGE

### Forward (direct) geocoding
- It's assumed that you have a CSV file with field(s) holding the address parts (or in a single field).
- Import the CSV file as a no-geometry table. Plugin will look for the fields' names and populate the combo boxes, so the user can define the fields that holds each address part. If some part is not available in the input table, user can select the corresponding option.
- Some addresses might not be found because of typo or missing address in the chosen service's database. If such problem occurs, the table lines not able to be geocoded will be saved in a separate CSV file. This can be selected in the 'Errors CSV output file' option.
- Click 'Geocode'. A new memory layer will be created after geocoding ends. Every field that exists in the input table will become a field in the new layer's attribute table.

### Reverse geocoding
- Straightforward: select a point layer, name the new field that will hold the address, and click 'Geocode'.

### NOTE
Remember to insert the required service parameters, or geocoding might fail.

### Contact
For suggestions, opinions or general contact, stay in touch:
- GitHub: http://github.com/diegobenincasa
- E-mail: diego@diegobenincasa.com
