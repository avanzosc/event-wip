.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=========================
Sale order renovate event
=========================
New scheduled "Renovate sales orders with contracts, and events". This new
scheduled selects sales orders that are associated with an event, and that are
also associated with a sales contract with the following contract conditions:

* In "open" state, type "contract", with recurring invoice, and her date end
  must be December 31st

The sales order, and her the contract will be duplicated, and the sales order
will automatically be confirmed, generating the event, registering the
employees, and confirming the records.

Credits
=======

Contributors
------------
* Ana Juaristi <anajuaristi@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
