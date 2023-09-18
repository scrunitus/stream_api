import subprocess
import typer
from typing import List, Optional
from enum import Enum
from logger import logger
from datetime import datetime

###########################
# --------- init -------- #
###########################

ALL_PWS = {}
app = typer.Typer(help="
run Oracle datapump Imports / Exports
")
date_now = datetime.now().strftime('%y-%m-%d_%H-%M-%S')

###########################
# --------- enum -------- #
###########################

class ExcludeInclude(str, Enum):
    constraint = "constraint"
    grant  = "grant"
    user = "user"
    schema = "schema"

class Mode(str, Enum):
    full = "full"
    tablespace  = "tablespace"
    schema = "schema"

class Compression(str, Enum):
    all = "all"
    data_only = "data_only"
    metadata_only = "metadata_only"
    none = "none"

###########################
# ------ callbacks ------ #
###########################

def _check_target_database_callback(ctx: typer.Context, param: typer.CallbackParam, value):
    print(ALL_PWS)

def _check_parallelity_callback(ctx: typer.Context, param: typer.CallbackParam, value):
    if value == 0:
        return 1
    if value >= 4:
        typer.confirm(f"Are you sure you want to run this job with a parallelity of {value}? ")
    return value

def _check_job_name(ctx: typer.Context, param: typer.CallbackParam, value):
    if value:
        return value
    return "datapump job"
   
###########################
# ------ functions ------ #
###########################

def get_passwords():
    return {"TKZ2Y01": "testPWtkz2y01", "PMAPS01": "pwpmaps"}

def run_datapump():
    subprocess.check_call()

def create_parfile(args: dict):
    datapump_args = ""
    for key in args.keys():
        datapump_args += f"{key}={args[key]}\n"
    with open(f"par_{date_now}.par", "w") as file:
        file.write(datapump_args)



###########################
# --------- main -------- #
###########################
@app.command()
def both(
        exclude_type: ExcludeInclude = typer.Option(None, "--exclude", "-et", help="exclude objects from datapump"),
        exclude_objects: Optional[List[str]] = typer.Option(None, "--exclude-objects", "-eo", help="The object names that will be excluded"),
        target_database_export: str = typer.Option(..., "--target-database-export", "-dbe", help="database where schema gets exportet from", callback=_check_target_database_callback),
        target_database_import: str = typer.Option(..., "--target-database-import", "-dbi", help="database where schema gets imported", callback=_check_target_database_callback),
        schemas: Optional[List[str]] = typer.Option(None, "--schemas", "-s", help="schemas to be exported"),
        tablespaces: Optional[List[str]] = typer.Option(None, "--tablespaces", "-tbl", help="tablespaces to be exported"),
        remap_schemas: Optional[List[str]] = typer.Option(None, "--remap-schemas", "-r", help="keep DDL structure of target schema and import the data only"),
        mode: Mode = typer.Option(..., "--mode", "-m", help="datapump mode"),
        compression: Compression = typer.Option(None, "--compression", "-co", help="run export in compression mode"),
        cluster: bool = typer.Option(None, "--cluster", "-cl", help="for RAC instance"),
        directory: str = typer.Option("DPDUMP", "--directory", "-dir", help="directory in which logfile / parfile / dumpfile will be saved"),
        dumpfile: str = typer.Option(f"EXP_{date_now}.dmp", "--dumpfile", "-dmp", help="name of the dumpfile"),
        parallel: int = typer.Option(1, "--parallel", "-p", help="uses multiple processes for the datapump job", callback=_check_parallelity_callback),      
        include_type: ExcludeInclude = typer.Option(None, "--include-type", "-it", help="include objects in datapump"),
        include_objects: Optional[List[str]] = typer.Option(None, "--include-objects", "-io", help="The object names that will be included"),
        job_name: str = typer.Option(None, "--job_name", "-job", help="the name of the datapump job sessions", callback=_check_job_name)
        ):
    """
    Runs export AND import
    """
    # ---------------------------------------------------
    #-------------- Check parameters --------------------#
    ######################################################
    if exclude_type and include_type:
        logger.error("you can't use include and exclude together!")
        raise typer.Abort()

    if mode == "schema" and not schemas and not remap_schemas:
        logger.error("Please specify the target schemas with --schemas or -s")
        raise typer.Abort()
    if mode == "schema" and tablespaces:
        logger.error("please remove option --tablespaces")
        raise typer.Abort()
    if mode == "tablespace" and not tablespaces:
        logger.error("Please specify the target tablespaces with --tablespaces or -tbl")
        raise typer.Abort()
    if mode == "tablespace" and schemas or mode == "tablespace" and remap_schemas:
        logger.error("please remove options --schemas / --remap-schemas ")
        raise typer.Abort()
   
    if remap_schemas:
        for schema_pair in remap_schemas:
            if not len(schema_pair.split(":")) == 2 or schema_pair.split(":")[1] == "":
                logger.error("please adjust the --remap-schema parameter: <exported_schema>:<target_import_schema>")
                raise typer.Abort()

    # ---------------------------------------------------
    #-------------- Append formated parameters to dict -> datapump_args
    ######################################################
    datapump_args = {}

    ################
    ### job_name ###
    ################
    datapump_args["JOB_NAME"] = f"\"{job_name}\""

    #################
    ### directory ###
    #################
    # TODO if given dir not available check available dirs on target host and display them
    datapump_args["DIRECTORY"] = directory

    ################
    ### dumpfile ###
    ################
    if parallel > 1:
        datapump_args["DUMPFILE"] = f"\"{dumpfile.split('.dmp')[0]}_%U.dmp\""
    else:
        datapump_args["DUMPFILE"] = f"\"{dumpfile}\""

    ################
    ### parallel ###
    ################
    datapump_args["PARALLEL"] = parallel

    ############
    ### mode ###
    ############
    if mode == "full":
        datapump_args["FULL"] = "Y"
    if mode == "schema" and schemas:
        result = ""
        for index, schema in enumerate(schemas):
            if index == 0:
                result += schema
            else:
                result += f",{schema}"
        datapump_args["SCHEMAS"] = result

    if mode == "tablespace" and tablespaces:
        result = ""
        for index, tablespace in enumerate(tablespaces):
            if index == 0:
                result += tablespace
            else:
                result += f",{tablespace}"
        datapump_args["TABLESPACES"] = result
   
    ####################
    ### remap schema ###
    ####################
    if remap_schemas:
        result = ""
        for index, schema_pair in enumerate(remap_schemas):
            if index == 0:
                result += schema_pair
            else:
                result += f",{schema_pair}"
        datapump_args["REMAP_SCHEMAS"] = result

    ###############
    ### exclude ###
    ###############
    if exclude_objects and not exclude_type:
        logger.error("please specify the exclude type with --exclude-type or -et")
        raise typer.Abort()
    if exclude_type:
        if exclude_objects:
            if len(exclude_objects) == 1:
                result = f"{exclude_type}:\"IN (\'{exclude_objects[0]}\')\""
            else:
                result = f"{exclude_type}:\""
                for index, obj in enumerate(exclude_objects):
                    if index + 1 == len(exclude_objects):
                        result += f", '{obj}')\""
                    elif index == 0:
                        result += f"IN ('{obj}'"
                    else:
                        result += f", '{obj}'"
        else:
            exclude_objects = []
            while True:
                if exclude_objects:
                    print(f"----- object list -----\n{exclude_objects}\n-----------------------")
                obj = input(f"Please specify the names of the excluded {exclude_type}s (leave blank when all objects are added): ")
                if obj == "" and not len(exclude_objects) == 0:
                    break
                if obj:
                    exclude_objects.append(obj.upper())
           
            if len(exclude_objects) == 1:
                result = f"{exclude_type}:\"IN (\'{exclude_objects[0]}\')\""
            else:
                result = f"{exclude_type}:\""
                for index, obj in enumerate(exclude_objects):
                    if index + 1 == len(exclude_objects):
                        result += f", '{obj}')\""
                    elif index == 0:
                        result += f"IN ('{obj}'"
                    else:
                        result += f", '{obj}'"

        datapump_args["EXCLUDE"] = result

    ###############
    ### include ###
    ###############
    if include_objects and not include_type:
        logger.error("please specify the include type with --include-type or -it")
        raise typer.Abort()
    if include_type:
        if include_objects:
            if len(include_objects) == 1:
                result = f"{include_type}:\"IN (\'{include_objects[0]}\')\""
            else:
                result = f"{include_type}:\""
                for index, obj in enumerate(include_objects):
                    if index + 1 == len(include_objects):
                        result += f", '{obj}')\""
                    elif index == 0:
                        result += f"IN ('{obj}'"
                    else:
                        result += f", '{obj}'"
        else:
            include_objects = []
            while True:
                if include_objects:
                    print(f"----- object list -----\n{include_objects}\n-----------------------")
                obj = input(f"Please specify the names of the included {include_type}s (leave blank when all objects are added): ")
                if obj == "" and not len(include_objects) == 0:
                    break
                if obj:
                    include_objects.append(obj.upper())
           
            if len(include_objects) == 1:
                result = f"{include_type}:\"IN (\'{include_objects[0]}\')\""
            else:
                result = f"{include_type}:\""
                for index, obj in enumerate(include_objects):
                    if index + 1 == len(include_objects):
                        result += f", '{obj}')\""
                    elif index == 0:
                        result += f"IN ('{obj}'"
                    else:
                        result += f", '{obj}'"
        datapump_args["INCLUDE"] = result

    ###################
    ### compression ###
    ###################
    if compression:
        datapump_args["COMPRESSION"] = compression.upper()

    ###############
    ### cluster ###
    ###############
    if cluster:
        datapump_args["CLUSTER"] = "YES"

    ######################
    ### create parfile ###
    ######################
    create_parfile(datapump_args)

@app.command()
def expdp():
    """
    Runs export
    """
    pass
@app.command()
def impdp():
    """
    Runs import
    """
    pass

if __name__ == "__main__":
    ALL_PWS = get_passwords()
   
    app()
