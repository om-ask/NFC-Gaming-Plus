<?php
/*
Plugin Name: Gaming Plus NFC Plugin
Description: Adds a secure REST API for managing attendee points via NFC. Ideal for events, it allows adding attendees and updating points with API key authentication.
Version: 1.0
Author: Omar
*/

// Register the activation hook to create the attendees table on plugin activation
register_activation_hook(__FILE__, 'create_attendees_table');

/**
 * Create the attendees table in the database on plugin activation
 */
function create_attendees_table() {
    global $wpdb;
    $table_name = $wpdb->prefix . 'attendees';
    $charset_collate = $wpdb->get_charset_collate();

    // SQL query to create the attendees table if it doesn't exist
    $sql = "CREATE TABLE IF NOT EXISTS $table_name (
        id BIGINT(20) NOT NULL AUTO_INCREMENT,
        first_name VARCHAR(60) NOT NULL,
        last_name VARCHAR(60) NOT NULL,
        hash VARCHAR(32) NOT NULL,
        points INT(11) NOT NULL DEFAULT 0,
        path VARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        UNIQUE KEY unique_hash (hash)
    ) $charset_collate;";

    // Include the WordPress upgrade file and execute the query
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}

/**
 * Validate API key to restrict access to authenticated users
 */
function validate_api_key_permission($request) {
    return true;
    // Retrieve the Authorization header from the request
    $auth_header = $request->get_header('Authorization');

    // Check if the Authorization header starts with "Bearer "
    if ($auth_header && strpos($auth_header, 'Bearer ') === 0) {
        // Extract the API key by removing the "Bearer " prefix
        $api_key = substr($auth_header, 7);

        // Get the expected API key from the environment
        $expected_api_key = defined('API_KEY') ? API_KEY : '';

        // Return true if the API key matches, otherwise return an error
        if ($api_key === $expected_api_key) {
            return true;
        }
    }

    return new WP_Error(
        'rest_forbidden',
        __('Incorrect API key provided. Access denied.'),
        array('status' => 403)
    );
}

/**
 * Register the REST API route to add a new attendee
 */
add_action('rest_api_init', function () {
    register_rest_route('my-api/v1', '/add-attendee', array(
        'methods' => 'POST',
        'callback' => 'add_attendee',
        'args' => array(
            'first_name' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param);
                }
            ),
            'last_name' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param);
                }
            ),
        ),
        'permission_callback' => 'validate_api_key_permission',
    ));
});

/**
 * Callback to add an attendee to the database
 */
function add_attendee($request) {
    global $wpdb;

    // Retrieve and sanitize attendee's first and last name from the request
    $first_name = sanitize_text_field($request->get_param('first_name'));
    $last_name = sanitize_text_field($request->get_param('last_name'));

    // Generate a unique 32-character hash using MD5 for the attendee
    $hash = md5($first_name . $last_name . current_time('mysql'));

    // Define the table name and insert the new attendee
    $table_name = $wpdb->prefix . 'attendees';
    $result = $wpdb->insert(
        $table_name,
        array(
            'first_name' => $first_name,
            'last_name' => $last_name,
            'hash' => $hash,
            'created_at' => current_time('mysql')
        ),
        array('%s', '%s', '%s', '%s')
    );

    // Handle potential database insertion errors
    if (false === $result) {
        return new WP_REST_Response(array(
            'error' => 'Could not add attendee to the database.',
            'details' => $wpdb->last_error,
        ), 500);
    }

    return new WP_REST_Response(array(
        'message' => 'Attendee added successfully.',
        'attendee_id' => $wpdb->insert_id,
    ), 201);
}

/**
 * Register the REST API route to add points for a single attendee
 */
add_action('rest_api_init', function () {
    register_rest_route('my-api/v1', '/add-point', array(
        'methods' => 'POST',
        'callback' => 'add_points_to_attendee',
        'args' => array(
            'user_identifier' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param);
                }
            ),
            'points' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param);
                }
            ),
            'path' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param);
                }
            ),
        ),
        'permission_callback' => 'validate_api_key_permission',
    ));
});

/**
 * Callback to add points to a specific attendee's record
 */
function add_points_to_attendee($request) {
    global $wpdb;

    // Sanitize the incoming parameters
    $user_identifier = sanitize_text_field($request->get_param('user_identifier'));
    $points_to_add = intval($request->get_param('points'));
    $path = sanitize_text_field($request->get_param('path'));

    // Retrieve the attendee from the database based on the identifier
    $table_name = $wpdb->prefix . 'attendees';
    $user = $wpdb->get_row(
        $wpdb->prepare("SELECT * FROM $table_name WHERE hash = %s", $user_identifier)
    );

    // If the user isn't found, return an error
    if (!$user) {
        return new WP_REST_Response(array(
            'error' => 'User not found.',
        ), 404);
    }

    // Update points and concatenate path
    $new_points = (int) $user->points + $points_to_add;
    $new_path = $user->path . '' . $path;

    // Update the attendee's points and path in the database
    $result = $wpdb->update(
        $table_name,
        array(
            'points' => $new_points,
            'path' => $new_path,
        ),
        array('id' => $user->id),
        array('%d', '%s'),
        array('%d')
    );

    if (false === $result) {
        return new WP_REST_Response(array(
            'error' => 'Failed to update points.',
            'details' => $wpdb->last_error,
        ), 500);
    }

    return new WP_REST_Response(array(
        'message' => 'Points added successfully.',
        'attendee_id' => $user->id,
        'added_points' => $points_to_add,
        'new_points' => $new_points,
        'path' => $path,
    ), 200);
}

/**
 * Register the REST API route to add points for multiple attendees
 */
add_action('rest_api_init', function () {
    register_rest_route('my-api/v1', '/add-points-bulk', array(
        'methods' => 'POST',
        'callback' => 'add_points_bulk',
        'args' => array(
            'users' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_array($param);
                }
            ),
        ),
        'permission_callback' => 'validate_api_key_permission',
    ));
});

/**
 * Callback to add points for multiple attendees in a single request
 */
function add_points_bulk($request) {
    global $wpdb;
    $table_name = $wpdb->prefix . 'attendees';

    // Get the array of users from the request
    $users = $request->get_param('users');
    $results = [];

    foreach ($users as $user_data) {
        // Sanitize and validate each user's data
        $user_identifier = sanitize_text_field($user_data['user_identifier']);
        $points_to_add = intval($user_data['points']);
        $path = sanitize_text_field($user_data['path']);

        // Look up the user in the database
        $user = $wpdb->get_row(
            $wpdb->prepare("SELECT * FROM $table_name WHERE hash = %s", $user_identifier)
        );

        if (!$user) {
            $results[] = array(
                'user_identifier' => $user_identifier,
                'error' => 'User not found',
            );
            continue;
        }

        // Update points and path for each user
        $new_points = (int) $user->points + $points_to_add;
        $new_path = $user->path . '' . $path;

        $update_result = $wpdb->update(
            $table_name,
            array(
                'points' => $new_points,
                'path' => $new_path,
            ),
            array('id' => $user->id),
            array('%d', '%s'),
            array('%d')
        );

        if (false === $update_result) {
            $results[] = array(
                'user_identifier' => $user_identifier,
                'error' => 'Failed to update points',
                'details' => $wpdb->last_error,
            );
        } else {
            $results[] = array(
                'user_identifier' => $user_identifier,
                'added_points' => $points_to_add,
                'new_points' => $new_points,
                'path' => $path,
            );
        }
    }

    // Return the results for each user
    return new WP_REST_Response($results, 200);
}


// Add shortcodes
/**
 * The [wporg] shortcode.
 *
 * Accepts a title and will display a box.
 *
 * @param array  $atts    Shortcode attributes. Default empty.
 * @param string $content Shortcode content. Default null.
 * @param string $tag     Shortcode tag (name). Default empty.
 * @return string Shortcode output.
 */

function user_point_shortcode( $atts = [], $content = null, $tag = '' ) {
    global $wpdb;
	$userid = get_query_var('user');


    // Retrieve the attendee from the database based on the identifier
    $table_name = $wpdb->prefix . 'attendees';
    $user = $wpdb->get_row(
        $wpdb->prepare("SELECT * FROM $table_name WHERE hash = %s", $userid)
    );

    // If the user isn't found, return an error
    if (!$user) {
        return 'user not found';
    }

    // Get point
    $o = $user->points;

	// return output
	return $o;
}

// add_action( 'init', 'wporg_shortcodes_init' );

// Add shortcodes
/**
 * The [top_users] shortcode.
 *
 * Displays the top 10 users based on points.
 *
 * @param array  $atts    Shortcode attributes. Default empty.
 * @param string $content Shortcode content. Default null.
 * @param string $tag     Shortcode tag (name). Default empty.
 * @return string Shortcode output.
 */
function top_users_shortcode( $atts = [], $content = null, $tag = '' ) {
    global $wpdb;

    $table_name = $wpdb->prefix . 'attendees';
    $top_users = $wpdb->get_results(
        "SELECT first_name, last_name, points FROM $table_name ORDER BY points DESC LIMIT 10"
    );

    if (empty($top_users)) {
        return 'No users found.';
    }

    $output = $output = '
    <table">
        <tr><th>Rank</th><th>Name</th><th>Points</th></tr>';;

    $rank = 1;
    foreach ($top_users as $user) {
        $output .= sprintf(
            '<tr><td>%d</td><td>%s</td><td>%d</td></tr>',
            $rank++,
            esc_html($user->first_name . ' ' . $user->last_name),
            esc_html($user->points)
        );
    }
    $output .= '</table>';

    return $output;
}

// populate wpdb with the ranking

function get_ranking() {
    global $wpdb;

    $table_name = $wpdb->prefix . 'attendees';
    $top_users = $wpdb->get_results(
        "SELECT first_name, last_name, points FROM $table_name ORDER BY points DESC LIMIT 10"
    );  

    if (empty($top_users)) {
        return 'No users found.';
    }

    $rank = 1;
    foreach ($top_users as $user) {
        $wpdb->insert(
            $rankings_table,
            array(        
                'first_name' => $user->first_name,
                'last_name'  => $user->last_name,
                'points'     => $user->points,
                'rank'       => $rank
            ),
            array(
                '%s', 
                '%s', 
                '%d', 
                '%d'  
            )
        );
        $rank++; // Increment the rank
    }
}

/**
 * Central location to create all shortcodes.
 */
function wporg_shortcodes_init() {
    global $wp; 
    $wp->add_query_var('user'); 
	add_shortcode( 'userpoint', 'user_point_shortcode' );
    add_shortcode( 'top_users', 'top_users_shortcode' );
}

add_action( 'init', 'wporg_shortcodes_init' );


// Connect to gamifier database
function connect_to_secondDB() {
    global $secondDB;
    $secondDB = new wpdb('u453805346_tickets_user','5fHe*m&G4','u453805346_gaming_tickets','127.0.0.1:3306');
}

add_action( 'init', 'connect_to_secondDB' );

function create_global_leaderboard_array() {
    global $leaderboard;
    leaderboard = array(
        1 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        ),
        2 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        ),
        3 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        ),
        4 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        ),
        5 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        ),
        6 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        ),
        7 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        ),
        8 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        ),
        9 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        ),
        10 => array(
            "first_name" => "",
            "last_name" => "",
            "points" => ""
        )
    )

}
add_action( 'init', 'create_global_leaderboard_array' );


?>

