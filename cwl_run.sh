# subprocess.Popen(['cwltoil','--jobStore',job_store_path, cwl_path, yaml_path])
cd $4
echo "$4"
echo "cwltoil --jobStore $3 $1 $2"
cwltoil --jobStore "$3" "$1" "$2"