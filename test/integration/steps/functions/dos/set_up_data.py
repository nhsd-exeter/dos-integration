from integration.steps.functions.utils import invoke_dos_db_handler_lambda


def set_up_palliative_care_in_db() -> None:
    """This function sets up the palliative care symptom discriminator.

    Setup in the symptomdisciminators table and in the symptomgroupsymptomdiscriminators table.
    """
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": "INSERT INTO pathwaysdos.symptomdiscriminators (id, description) VALUES (14167, 'Pharmacy Palliative Care Medication Stockholder') ON CONFLICT DO NOTHING RETURNING id",  # noqa: E501
            "query_vars": None,
        },
    )
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": "INSERT INTO pathwaysdos.symptomgroupsymptomdiscriminators (id, symptomgroupid, symptomdiscriminatorid) VALUES (10000, 360, 14167) ON CONFLICT DO NOTHING RETURNING id",  # noqa: E501
            "query_vars": None,
        },
    )


def set_up_blood_pressure_z_code_in_db() -> None:
    """This function sets up the blood pressure symptom discriminator.

    Setup in the symptomdisciminators table and in the symptomgroupsymptomdiscriminators table.
    """
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": "INSERT INTO pathwaysdos.symptomdiscriminators (id, description) VALUES (14207, 'Blood Pressure') ON CONFLICT DO NOTHING RETURNING id",  # noqa: E501
            "query_vars": None,
        },
    )
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": "INSERT INTO pathwaysdos.symptomgroupsymptomdiscriminators (id, symptomgroupid, symptomdiscriminatorid) VALUES (10001, 360, 14207) ON CONFLICT DO NOTHING RETURNING id",  # noqa: E501
            "query_vars": None,
        },
    )


def set_up_contraception_z_code_in_db() -> None:
    """This function sets up the blood pressure symptom discriminator.

    Setup in the symptomdisciminators table and in the symptomgroupsymptomdiscriminators table.
    """
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": "INSERT INTO pathwaysdos.symptomdiscriminators (id, description) VALUES (14210, 'Contraception') ON CONFLICT DO NOTHING RETURNING id",  # noqa: E501
            "query_vars": None,
        },
    )
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": "INSERT INTO pathwaysdos.symptomgroupsymptomdiscriminators (id, symptomgroupid, symptomdiscriminatorid) VALUES (10002, 360, 14210) ON CONFLICT DO NOTHING RETURNING id",  # noqa: E501
            "query_vars": None,
        },
    )


def set_up_common_condition_service_types() -> None:
    """This function sets up the common condition service types."""
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": """INSERT INTO pathwaysdos.servicetypes (id, "name", nationalranking, searchcapacitystatus, capacitymodel, capacityreset) VALUES(148, 'NHS Community Blood Pressure Check service', '1', true, NULL, 'interval') ON CONFLICT DO NOTHING RETURNING id""",  # noqa: E501
            "query_vars": None,
        },
    )
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": """INSERT INTO pathwaysdos.servicetypes (id, "name", nationalranking, searchcapacitystatus, capacitymodel, capacityreset) VALUES(149, 'NHS Community Pharmacy Contraception service', '1', true, NULL, 'interval') ON CONFLICT DO NOTHING RETURNING id""",  # noqa: E501
            "query_vars": None,
        },
    )
