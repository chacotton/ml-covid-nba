"""Module of SQL Templates for selecting best logged model from database"""
from string import Template

VALID_MODELS = Template("SELECT `key`,run_uuid FROM tags WHERE `value` = '$type';")

BEST_PERFORMANCE = Template("SELECT run_uuid FROM metrics where run_uuid in ($run_ids) AND `key` "
                            "LIKE '%%$metric%%' ORDER BY `value` DESC LIMIT 1;")

PARAMS = Template("SELECT `key`,`value` FROM params where run_uuid = '$run_id';")

METRICS = Template("SELECT `key`,`value` FROM metrics where run_uuid = '$run_id';")

CLASS = Template("SELECT `value` FROM tags WHERE run_uuid = '$run_id' AND `key` = 'estimator_class';")
