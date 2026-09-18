# Generating JBrowse1 tracks from repeat annotation GFF3

This CWL workflow takes a RepeatModeler or EarlGrey GFF3 file, rewrites it into a JBrowse1-friendly parent/child structure, and converts the result into a JBrowse JSON track directory.

## Inputs

The workflow accepts a YAML file with these inputs:

```yaml
repeat_annotations:
    class: File
    path: /Users/files/test.gff
singularity_image: /project/nal_genomics/shared_programs/jbrowse_1.16.11--pl5321h9f5acd7_5.sif
annotation_source: EarlGrey
data_provider: "Jane Doe, USDA-ARS"
data_source: "doi:/10.adc/1235"
data_description: "Repeat annotations converted for JBrowse1"
materials_and_methods: "Repeat Modeler v1.2 was run with default parameters"
publication_status: "Published, please cite doi:/10.adc/1235"
track_name: "Repeat trakcs "
jbrowse_directory: /project/nal_genomics/jbrowse/amel/data
```

`repeat_annotations` is the input GFF3 file.

`singularity_image` is the JBrowse1 container image.

`annotation_source` controls how the GFF is interpreted. Use `EarlGrey` for EarlGrey input and `RepeatModeler` for RepeatModeler input. If omitted, the workflow treats the file as EarlGrey.

`data_provider`, `data_source`, `data_description`, `materials_and_methods`, and `publication_status` are written into the JBrowse metadata stanza.

`track_name` populates the JBrowse track label and display key.

`jbrowse_directory` is optional. If it is provided, it must be an absolute path, and the workflow copies the generated files into that JBrowse directory.

When publishing into an existing JBrowse directory, the helper merges `trackList.json` by track label instead of overwriting the whole file.

The workflow now returns a small JSON summary file instead of the full generated directory tree. If `jbrowse_directory` is omitted, the generated JSON directory is only staged internally during workflow execution and may be cleaned up by `cwltool` after the run finishes.

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

Create a copy of repeatmodeler_params.yml, and edit it for your use case.

Run the workflow with cwltool:

```bash
cwltool repeatmodeler_workflow.cwl repeatmodeler_params.yml
```

The workflow first runs [tools/remodel-repeats.py](/Users/mpoelchau/Documents/programs/repeats_to_jbrowse/tools/remodel-repeats.py) on the input GFF3 file, then runs `flatfile-to-json.pl` inside the supplied JBrowse1 container, and finally copies the generated JSON files into `jbrowse_directory` when that optional input is supplied.

For EarlGrey input, the rendered features are colored by type prefix using these categories: LINE, SINE, DNA, LTR, RC, Low_complexity, Satellite, Simple_repeat, and Unknown.
