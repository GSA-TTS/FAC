# These are our active APIs
# admin_api_access_tables must run before
# the admin API can be stood up.
declare -a sql_pre_scripts=(
    "api_v1_0_3" 
    "api_v1_1_0"
    "admin_api_access_tables"
    "admin_api_v1_1_0"
    "admin_api_v1_1_1"
    "public_api_v1_0_0"
    "public_data_v1_0_0"
    # We need some of this for the 
    # copying of data from DB1 to DB2.
    # Specifically, schemas, roles, permissions, and sequences.
    "schemas"
    "roles"
    "permissions"
    "sequences"
    "finalize"
)

declare -a sql_post_scripts=(
    "api_v1_0_3" 
    "api_v1_1_0"
    "admin_api_access_tables"
    "admin_api_v1_1_0"
    "admin_api_v1_1_1"
    "public_api_v1_0_0"
    "public_data_v1_0_0"
    "permissions"
    "finalize"
    )    


# # These are the tables that must be present
# # in order to stand up that API.
# declare -a api_required_tables=(
#   "public.dissemination_general"
#   "public.dissemination_general"
#   "public.support_adminapievent"
#   "public.support_administrative_key_uuids"
#   "public.support_administrative_key_uuids"
#   "public_data_v1_0_0.general"
#   "public.dissemination_general"
# )

declare -a indexes=(
    "additional_eins"
    "additional_ueis"
    "combined"
    "corrective_action_plans"
    "federal_awards"
    "findings"
    "findings_text"
    "general"
    "notes_to_sefa"
    "passthrough"
    "secondary_auditors"
)

# declare -a db2_indexes_required_tables=(
#     "public_data_v1_0_0.additional_eins"
#     "public_data_v1_0_0.additional_ueis"
#     "public_data_v1_0_0.combined"
#     "public_data_v1_0_0.corrective_action_plans"
#     "public_data_v1_0_0.federal_awards"
#     "public_data_v1_0_0.findings"
#     "public_data_v1_0_0.findings_text"
#     "public_data_v1_0_0.general"
#     "public_data_v1_0_0.notes_to_sefa"
#     "public_data_v1_0_0.passthrough"
#     "public_data_v1_0_0.secondary_auditors"
# )
