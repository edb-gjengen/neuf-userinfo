<?php
require_once("/var/www/studentersamfundet.no/www/wp/wp-load.php");

$filename = $argv[1];
$json = file_get_contents($filename);
$users = json_decode($json);
foreach($users as $user) {
        list($username,$first_name,$last_name, $email) = $user;
        $pass = wp_generate_password( $length=32);
        $userdata = array(
                'user_login' => $username,
                'user_pass' => $pass,
                'first_name' => $first_name,
                'last_name' => $last_name);
        $user_id = username_exists( $username );
        if ( !$user_id ) {
                $user_id = wp_insert_user($userdata);
                echo "[new] $user_id : $username,$first_name,$last_name\n";
        } else {
                //echo "$user_id\n";
        }
}
