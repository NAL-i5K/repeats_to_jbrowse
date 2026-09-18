# Generating JBrowse1 tracks from RepeatModeler annotations

This CWL workflow takes a RepeatModeler GFF3 file, rewrites it into a JBrowse1-friendly parent/child structure, and converts the result into a JBrowse JSON track directory.

## Inputs

The workflow accepts a YAML file with these inputs:

```yaml
repeat_annotations:
    class: File
    path: /Users/files/test.gff
singularity_image: /project/nal_genomics/shared_programs/jbrowse_1.16.11--pl5321h9f5acd7_5.sif
data_provider: "Jane Doe, USDA-ARS"
data_source: "doi:/10.adc/1235"
materials_and_methods: "Repeat Modeler v1.2 was run with default parameters"
publication_status: "Published, please cite doi:/10.adc/1235"
track_name: "Repeat trakcs "
jbrowse_directory: /project/nal_genomics/jbrowse/amel/data
```

`repeat_annotations` is the input RepeatModeler GFF3 file.

`singularity_image` is the JBrowse1 container image.

`data_provider`, `data_source`, `materials_and_methods`, and `publication_status` are written into the JBrowse metadata stanza.

`track_name` populates the JBrowse track label and display key.

`jbrowse_directory` is optional. The workflow always stages JSON into `repeatmodeler_json_tracks` in the CWL working directory. If `jbrowse_directory` is provided, it must be an absolute path, and the workflow then copies those generated files into that JBrowse directory.

When publishing into an existing JBrowse directory, the helper merges `trackList.json` by track label instead of overwriting the whole file.

## Usage

If running this workflow on Ceres, first create a conda environment: 

```bash
conda create --name cwltool-env
conda activate cwltool-env
conda install -c conda-forge cwltool -y
conda install -c conda-forge nodejs
```

Load the environment:

```bash
module load apptainer
module load miniconda
conda activate cwltool-env
```

Run the workflow with cwltool:

```bash
cwltool repeatmodeler_workflow.cwl repeatmodeler_params.yml
```

`cwltool` writes the workflow output object to standard output when the run completes. For this workflow, that means the generated `json_tracks` directory can be rendered as a large JSON blob. If you want to keep the normal progress logging but suppress that final JSON, redirect standard output and leave standard error alone:

```bash
cwltool repeatmodeler_workflow.cwl repeatmodeler_params.yml > /dev/null
```

If you want to capture the output object instead of printing it to the terminal, redirect it to a file:

```bash
cwltool repeatmodeler_workflow.cwl repeatmodeler_params.yml > workflow-output.json
```

The workflow first runs [tools/remodel-repeats.py](/Users/mpoelchau/Documents/programs/repeats_to_jbrowse/tools/remodel-repeats.py) on the input GFF3 file, then runs `flatfile-to-json.pl` inside the supplied JBrowse1 container, and finally copies the generated JSON files into `jbrowse_directory` when that optional input is supplied.
