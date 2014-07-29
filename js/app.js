define(function(require) {
	var $ = require('jquery'),
		enums = require('enums'),
		network = require('network'),
		pubsub = require('pubsub'),
		current_page = null,
		periodic_resize_check_width = null,
		periodic_resize_check_height = null,
		got_local_storage = 'localStorage' in window,
		showPage = function(page) {
			if (page !== current_page) {
				$('.page').hide();
				$('#page-' + page).show();

				if (page === 'login') {
					$('#login-form-username').focus();
				}

				current_page = page;

				pubsub.publish(enums.PubSub.Client_SetPage, page);
			}
		},
		checkBrowserSupport = function() {
			if (network.isBrowserSupported()) {
				$('#section-login-form').show();
			} else {
				$('#section-websockets-not-supported').show();
			}
		},
		periodicResizeCheck = function() {
			var width = $(window).width(),
				height = $(window).height();

			if (width !== periodic_resize_check_width || height !== periodic_resize_check_height) {
				periodic_resize_check_width = width;
				periodic_resize_check_height = height;
				pubsub.publish(enums.PubSub.Client_Resize, width, height);
			}

			setTimeout(periodicResizeCheck, 500);
		},
		initializeUsername = function() {
			var username;

			if (got_local_storage) {
				username = localStorage['username'];
				if (typeof username !== 'undefined') {
					$('#login-form-username').val(username);
				}
			}
		},
		onSubmitLoginForm = function() {
			var username = $('#login-form-username').val().replace(/\s+/g, ' ').trim();

			if (username.length === 0 || username.length > 32) {
				onServerFatalError(enums.FatalErrors.InvalidUsername);
			} else {
				if (got_local_storage) {
					localStorage['username'] = username;
				}

				showPage('connecting');
				$('#login-error-message').html($('<p>').text('Lost connection to the server.'));
				network.connect(username);
			}

			return false;
		},
		onClientSetClientData = function() {
			showPage('lobby');
		},
		onServerFatalError = function(fatal_error_id) {
			var message;

			if (fatal_error_id === enums.FatalErrors.NotUsingLatestVersion) {
				message = 'You are not using the latest version. Please reload this page to get it!';
			} else if (fatal_error_id === enums.FatalErrors.InvalidUsername) {
				message = 'Invalid username. Username must have between 1 and 32 characters.';
			} else if (fatal_error_id === enums.FatalErrors.UsernameAlreadyInUse) {
				message = 'Username already in use.';
			} else {
				message = 'Unknown error.';
			}

			$('#login-error-message').html($('<p>').text(message));
		},
		onClientSetOption = function(key, value) {
			if (key === 'enable-high-contrast-colors') {
				if (value) {
					$('body').addClass('high-contrast');
				} else {
					$('body').removeClass('high-contrast');
				}
			}
		},
		onClientJoinGame = function() {
			showPage('game');
		},
		onClientLeaveGame = function() {
			showPage('lobby');
		},
		onNetworkClose = function() {
			showPage('login');
		},
		onNetworkError = function() {
			$('#login-error-message').html($('<p>').text('Could not connect to the server.'));
			showPage('login');
		};

	require('heartbeat');
	require('lobby');
	require('game');

	checkBrowserSupport();
	periodicResizeCheck();
	initializeUsername();
	showPage('login');

	$('#login-form').submit(onSubmitLoginForm);

	pubsub.subscribe(enums.PubSub.Client_SetClientData, onClientSetClientData);
	pubsub.subscribe(enums.PubSub.Server_FatalError, onServerFatalError);
	pubsub.subscribe(enums.PubSub.Client_SetOption, onClientSetOption);
	pubsub.subscribe(enums.PubSub.Client_JoinGame, onClientJoinGame);
	pubsub.subscribe(enums.PubSub.Client_LeaveGame, onClientLeaveGame);
	pubsub.subscribe(enums.PubSub.Network_Close, onNetworkClose);
	pubsub.subscribe(enums.PubSub.Network_Error, onNetworkError);

	pubsub.publish(enums.PubSub.Client_InitializationComplete);
});
