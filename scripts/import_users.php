<?php

$filename = $argv[1];
$wp_load_path = $argv[2];
require_once($wp_load_path);

$site_name = get_bloginfo('name');

$json = file_get_contents($filename);
$users = json_decode($json);
foreach($users as $user) {
        list($username,$first_name,$last_name, $email) = $user;
        $pass = wp_generate_password( $length=32);
        $userdata = array(
                'user_login' => $username,
                'user_pass' => $pass,
                'user_email' => $email,
                'first_name' => $first_name,
                'last_name' => $last_name);
        $user_id = username_exists( $username );
        if ( !$user_id ) {
                $user_id = wp_insert_user($userdata);
                echo "[$site_name][new] $user_id : $username,$first_name,$last_name,$email\n";
                /* LDAP login flag */
                $flagged = add_user_meta( $user_id, "wpDirAuthFlag", "1");
                echo $flagged == false ? "\t$user_id not flagged\n" : "";

        }
}
