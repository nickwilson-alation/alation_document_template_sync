# alation_document_template_sync

How It Works:
* The script uses a "primary" -> "child" model to sync all templates and their associated configurations
* The "primary" set of templates are considered the desired end-state for all child document hubs and their template sets
* Basically, what is in the "primary" document hub will be mirrored by the other Glossary document hubs

Setup:
* Create a new Document Hub called "Primary Glossary Templates", which will be the "primary" Glossary hub, containing the primary templates
* For each Glossary to be synced to the primary, create a new Document Hub, and ensure that its title ends with " Glossary" (note the space preceding the word 'Glossary')
* Create the desired set of primary templates under the "Primary Glossary Templates" Document Hub
* Run the script to sync from the primary to the child Glossary Document Hubs

FAQ:

Q: What if a template is created on a child glossary, and it gets used by a document?
A: The script will be unable to delete the template until the document is assigned to another template.