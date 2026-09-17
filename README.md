# Generating JBrowse1 tracks from RepeatModeler annotations

This CWL workflow takes a RepeatModeler GFF3 file, rewrites it into a JBrowse1-friendly parent/child structure, and converts the result into a JBrowse JSON track directory.

## Inputs

The workflow accepts a YAML file with these inputs:

```yaml
repeat_annotations:
    class: File
    path: /Users/mpoelchau/Downloads/test.gff
singularity_image: /project/nal_genomics/shared_programs/jbrowse_1.16.11--pl5321h9f5acd7_5.sif
data_provider: "Monica Poelchau, USDA-ARS"
data_source: "doi:/10.adc/1235"
materials_and_methods: "Repeat Modeler v1.2 was run with default parameters"
publication_status: "Published"
track_name: "Ontophagus taurus repeats"
jbrowse_directory: /project/nal_genomics/jbrowse/amel/data
```

`repeat_annotations` is the input RepeatModeler GFF3 file.

`singularity_image` is the JBrowse1 container image.

`data_provider`, `data_source`, `materials_and_methods`, and `publication_status` are written into the JBrowse metadata stanza.

`track_name` populates the JBrowse track label and display key.

`jbrowse_directory` is optional. If omitted, the workflow writes into `repeatmodeler_json_tracks` in the working directory.

## Usage

Run the workflow with cwltool:

```bash
cwltool repeatmodeler_workflow.cwl repeatmodeler_params.yml
```

The workflow first runs [remodel-repeats.py](../remodel-repeats.py) on the input GFF3 file, then runs `flatfile-to-json.pl` inside the supplied JBrowse1 container.
