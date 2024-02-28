<?php
$new_role_id = $_REQUEST["n"];
echo shell_exec("import app; app.edit_role_id() '$new_role_id'")
?>