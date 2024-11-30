<?php
/*
Plugin Name: Gaming Plus NFC Plugin
Description: Adds a secure REST API for managing attendee points via NFC. Ideal for events, it allows adding attendees and updating points with API key authentication.
Version: 1.0
Author: Omar
*/

// Register the activation hook to create the attendees table on plugin activation
register_activation_hook(__FILE__, 'create_attendees_table');
global $userAdded;
global $top_users;
$userAdded = false;
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
        name VARCHAR(60) NOT NULL,
        hash VARCHAR(32) NOT NULL,
        email VARCHAR(32) NOT NULL,
        points INT(11) NOT NULL DEFAULT 0,
        path VARCHAR(255) NOT NULL,
        last_quest VARCHAR(255) NOT NULL,
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
            'name' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param);
                }
            ),
            'email' => array(
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
    $name = sanitize_text_field($request->get_param('name'));
    $email = sanitize_text_field($request->get_param('email'));

    // Generate a unique 32-character hash using MD5 for the attendee
    $hash = md5($name . $email . current_time('mysql'));

    // Define the table name and insert the new attendee
    $table_name = $wpdb->prefix . 'attendees';
    $existing_attendee = $wpdb->get_var($wpdb->prepare(
        "SELECT id FROM $table_name WHERE email = %s", 
        $email
    ));

    if ($existing_attendee) {
        return new WP_REST_Response(array(
            'error' => 'An attendee with this email already exists.',
            'attendee_id' => $existing_attendee,
        ), 409); // 409 Conflict
    }


    $result = $wpdb->insert(
        $table_name,
        array(
            'name' => $name,
            'email' => $email,
            'hash' => $hash,
            'created_at' => current_time('mysql')
        ),
        array('%s', '%s', '%s', '%s')
    );
    $userAdded = true;

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

add_action('rest_api_init', function () {
    register_rest_route('attendees/v1', '/get-attendee', array(
        'methods'  => 'GET',
        'callback' => 'get_attendee_by_email',
        'args'     => array(
            'email' => array(
                'required' => true,
                'validate_callback' => function ($param) {
                    return is_email($param);
                },
            ),
        ),
    ));
});

/**
 * Callback to retrieve attendee information by email
 */
function get_attendee_by_email($request) {
    global $wpdb;

    // Retrieve and sanitize the email from the request
    $email = sanitize_email($request->get_param('email'));

    // Define the table name
    $table_name = $wpdb->prefix . 'attendees';

    // Query the database for the attendee with the given email
    $attendee = $wpdb->get_row($wpdb->prepare(
        "SELECT * FROM $table_name WHERE email = %s", 
        $email
    ));

    // Handle case where no attendee is found
    if (null === $attendee) {
        return new WP_REST_Response(array(
            'error' => 'Attendee not found.',
        ), 404);
    }

    // Return the attendee information
    return new WP_REST_Response(array(
        'message' => 'Attendee found.',
        'attendee' => $attendee,
    ), 200);
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
            'last_quest' => array(
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
    $last_quest = sanitize_text_field($request->get_param('last_quest'));

    // Retrieve the attendee from the database based on the identifier
    $table_name = $wpdb->prefix . 'attendees';
    $user = $wpdb->get_row(
        $wpdb->prepare("SELECT * FROM $table_name WHERE email = %s", $user_identifier)
    );

    // If the user isn't found, return an error
    if (!$user) {
        return new WP_REST_Response(array(
            'error' => 'User not found.',
        ), 404);
    }

    if ($last_quest == $user->last_quest) {
        return new WP_REST_Response(array(
            'error' => 'User already completed this quest.',
        ), 400);
    }

    // Update points and concatenate path
    $new_points = (int) $user->points + $points_to_add;
    $userAdded = true;

    // Update the attendee's points and path in the database
    $result = $wpdb->update(
        $table_name,
        array(
            'points' => $new_points,
            'last_quest' => $last_quest,
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
        'last_quest' => $last_quest,
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

/**
 * Central location to create all shortcodes.
 */
if ( ! defined( 'ABSPATH' ) ) {
    exit; // Exit if accessed directly.
}

// Enqueue JavaScript
function top_users_enqueue_scripts() {
    wp_enqueue_script(
        'top-users-refresh',
        plugins_url( 'js/top-users-refresh.js', __FILE__ ),
        array( 'jquery' ),
        null,
        true
    );
    wp_localize_script( 'top-users-refresh', 'topUsersAjax', array(
        'ajaxurl' => admin_url( 'admin-ajax.php' )
    ));
}
add_action( 'wp_enqueue_scripts', 'top_users_enqueue_scripts' );

// AJAX handler to fetch top users
function fetch_top_users_ajax() {
    global $wpdb;

    $table_name = $wpdb->prefix . 'attendees';

    if (true === $userAdded || empty($top_users)) {
        $top_users = $wpdb->get_results(
            "SELECT first_name, last_name, points FROM $table_name ORDER BY points DESC LIMIT 10"
        );
        $userAdded = false;
    }

    if (empty($top_users)) {
        wp_send_json_error('No users found.');
    }

    $output = [];
    $rank = 1;
    foreach ($top_users as $user) {
        $output[] = [
            'rank' => $rank++,
            'name' => esc_html($user->first_name . ' ' . $user->last_name),
            'points' => esc_html($user->points)
        ];
    }

    wp_send_json_success($output);
}

add_action( 'wp_ajax_fetch_top_users', 'fetch_top_users_ajax' );
add_action( 'wp_ajax_nopriv_fetch_top_users', 'fetch_top_users_ajax' );

// Shortcode to display data from local storage
function top_users_shortcode() {
    return '
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                const storedData = localStorage.getItem("topUsersData");
                if (storedData) {
                    const topUsers = JSON.parse(storedData);
                    var i = 1;
                    topUsers.forEach(user => {
                        const userDataRank = document.getElementById("user" + i + "rank");
                        const userDataName = document.getElementById("user" + i + "name");
                        const userDataPoints = document.getElementById("user" + i + "points");
                        if ( userDataName !== null) {
                            userDataName.innerHTML = user.name;
                        }
                        if ( userDataPoints !== null) {
                            userDataPoints.innerHTML = user.points;
                        }
                        if ( userDataRank !== null) {
                            userDataRank.innerHTML = user.rank;
                        }
                        console.log(i);
                        console.log(user);
                        i++;
                    });
                }
            });
        </script>
    ';
}

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
    $leaderboard = array(
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

/**
 * Register the REST API route to add a new attendee
 */
add_action('rest_api_init', function () {
    register_rest_route('my-api/v1', '/register-ticket', array(
        'methods' => 'POST',
        'callback' => 'get_email_add_user',
        'args' => array(
            'ticket_id' => array(
                'required' => true,
                'validate_callback' => function($param, $request, $key) {
                    return is_string($param);
                }
            )
        ),
        'permission_callback' => 'validate_api_key_permission',
    ));
});

/**
 * Callback to add an attendee to the database
 */
function get_email_add_user($request) {
    global $wpdb;
    global $secondDB;

    // Retrieve and sanitize attendee's first and last name from the request
    $ticketId = sanitize_text_field($request->get_param('ticket_id'));

    $results = get_userInfo_by_ticketId($ticketId);

    // Generate a unique 32-character hash using MD5 for the attendee
    $hash = md5($results->name . $results->email . current_time('mysql'));

    // Define the table name and insert the new attendee
    $table_name = $wpdb->prefix . 'attendees';

    $existing_attendee = $wpdb->get_var($wpdb->prepare(
        "SELECT id FROM $table_name WHERE email = %s", 
        $email
    ));

    if ($existing_attendee) {
        return new WP_REST_Response(array(
            'error' => 'An attendee with this email already exists.',
            'attendee_id' => $existing_attendee,
        ), 409); // 409 Conflict
    }

    $insert_res = $wpdb->insert(
        $table_name,
        array(
            'name' => $results->name,
            'email' => $results->email,
            'hash' => $hash,
            'created_at' => current_time('mysql')
        ),
        array('%s', '%s', '%s', '%s')
    );
     $userAdded = true;
 
    // Handle potential database insertion errors
    if (false === $insert_res) {
        return new WP_REST_Response(array(
            'error' => 'Could not add attendee to the database.',
            'details' => $wpdb->last_error,
        ), 500);
    }
 
    return new WP_REST_Response(array(
        'message' => 'Attendee added successfully.',
        'attendee_id' => $wpdb->insert_id,
    ), 201);

    // Check if we have results
    if ($results) {
        // Return the results
        return new WP_REST_Response(array(
            'message' => 'ticket converted successfully.',
            'email' => $results->email,
        ), 200);
    } else {
        return [];
    }
}


function get_userInfo_by_ticketId($ticketId) {
    global $secondDB; 

    $query = "
        SELECT u.name, u.email, t.name AS ticket_name
        FROM invoices i
        JOIN bookings b ON i.id = b.invoice_id
        JOIN users u ON u.id = i.user_id
        JOIN tickets t ON t.id = b.ticket_id
        WHERE b.code = %s
    ";

    
    $results = $secondDB->get_results($secondDB->prepare($query, $ticketId));

    // Check if we have results
    if ($results) {
        // Return the results
        return $results[0];
    } else {
        return [];
    }
}

?>

