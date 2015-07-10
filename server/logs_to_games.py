#!/usr/bin/env python3.4m

import enums
import inspect
import pickle
import random
import re
import server
import traceback
import ujson
import util


class Enums:
    lookups = {
        'CommandsToClient': [
            'FatalError',
            'SetClientId',
            'SetClientIdToData',
            'SetGameState',
            'SetGameBoardCell',
            'SetGameBoard',
            'SetScoreSheetCell',
            'SetScoreSheet',
            'SetGamePlayerJoin',
            'SetGamePlayerRejoin',
            'SetGamePlayerLeave',
            'SetGamePlayerJoinMissing',
            'SetGameWatcherClientId',
            'ReturnWatcherToLobby',
            'AddGameHistoryMessage',
            'AddGameHistoryMessages',
            'SetTurn',
            'SetGameAction',
            'SetTile',
            'SetTileGameBoardType',
            'RemoveTile',
            'AddGlobalChatMessage',
            'AddGameChatMessage',
            'DestroyGame',
            # defunct
            'SetGamePlayerUsername',
            'SetGamePlayerClientId',
        ],
        'CommandsToServer': [
            'CreateGame',
            'JoinGame',
            'RejoinGame',
            'WatchGame',
            'LeaveGame',
            'DoGameAction',
            'SendGlobalChatMessage',
            'SendGameChatMessage',
        ],
        'Errors': [
            'NotUsingLatestVersion',
            'GenericError',
            'InvalidUsername',
            'InvalidPassword',
            'MissingPassword',
            'ProvidedPassword',
            'IncorrectPassword',
            'NonMatchingPasswords',
            'ExistingPassword',
            'UsernameAlreadyInUse',
            'LostConnection',
        ],
        'GameActions': [
            'StartGame',
            'PlayTile',
            'SelectNewChain',
            'SelectMergerSurvivor',
            'SelectChainToDisposeOfNext',
            'DisposeOfShares',
            'PurchaseShares',
            'GameOver',
        ],
        'GameBoardTypes': [
            'Luxor',
            'Tower',
            'American',
            'Festival',
            'Worldwide',
            'Continental',
            'Imperial',
            'Nothing',
            'NothingYet',
            'CantPlayEver',
            'IHaveThis',
            'WillPutLonelyTileDown',
            'HaveNeighboringTileToo',
            'WillFormNewChain',
            'WillMergeChains',
            'CantPlayNow',
            'Max',
        ],
        'GameHistoryMessages': [
            'TurnBegan',
            'DrewPositionTile',
            'StartedGame',
            'DrewTile',
            'HasNoPlayableTile',
            'PlayedTile',
            'FormedChain',
            'MergedChains',
            'SelectedMergerSurvivor',
            'SelectedChainToDisposeOfNext',
            'ReceivedBonus',
            'DisposedOfShares',
            'CouldNotAffordAnyShares',
            'PurchasedShares',
            'DrewLastTile',
            'ReplacedDeadTile',
            'EndedGame',
            'NoTilesPlayedForEntireRound',
            'AllTilesPlayed',
        ],
        'GameModes': [
            'Singles',
            'Teams',
            'Max',
        ],
        'GameStates': [
            'Starting',
            'StartingFull',
            'InProgress',
            'Completed',
        ],
        'Notifications': [
            'GameFull',
            'GameStarted',
            'YourTurn',
            'GameOver',
        ],
        'Options': [
            'EnablePageTitleNotifications',
            'EnableSoundNotifications',
            'Sound',
            'EnableHighContrastColors',
            'EnableTextBackgroundColors',
            'ColorScheme',
            'GameBoardLabelMode',
        ],
        'ScoreSheetIndexes': [
            'Luxor',
            'Tower',
            'American',
            'Festival',
            'Worldwide',
            'Continental',
            'Imperial',
            'Cash',
            'Net',
            'Username',
            'PositionTile',
            'Client',
        ],
        'ScoreSheetRows': [
            'Player0',
            'Player1',
            'Player2',
            'Player3',
            'Player4',
            'Player5',
            'Available',
            'ChainSize',
            'Price',
        ]
    }

    _lookups_changes = {
        1417176502: {
            'CommandsToClient': [
                'FatalError',
                'SetClientId',
                'SetClientIdToData',
                'SetGameState',
                'SetGameBoardCell',
                'SetGameBoard',
                'SetScoreSheetCell',
                'SetScoreSheet',
                'SetGamePlayerUsername',
                'SetGamePlayerClientId',
                'SetGameWatcherClientId',
                'ReturnWatcherToLobby',
                'AddGameHistoryMessage',
                'AddGameHistoryMessages',
                'SetTurn',
                'SetGameAction',
                'SetTile',
                'SetTileGameBoardType',
                'RemoveTile',
                'AddGlobalChatMessage',
                'AddGameChatMessage',
                'DestroyGame',
            ],
        },
        1409233190: {
            'Errors': [
                'NotUsingLatestVersion',
                'InvalidUsername',
                'UsernameAlreadyInUse',
            ],
        },
    }

    _translations = {}

    @staticmethod
    def initialize():
        for timestamp, changes in Enums._lookups_changes.items():
            translation = {}
            for enum_name, entries in changes.items():
                entry_to_new_index = {entry: index for index, entry in enumerate(Enums.lookups[enum_name])}
                old_index_to_new_index = {index: entry_to_new_index[entry] for index, entry in enumerate(entries)}
                translation[enum_name] = old_index_to_new_index
            Enums._translations[timestamp] = translation

    @staticmethod
    def get_translations(timestamp=None):
        if timestamp is None:
            return {}

        translations_for_timestamp = {}
        for trans_timestamp, trans_changes in sorted(Enums._translations.items(), reverse=True):
            if timestamp <= trans_timestamp:
                translations_for_timestamp.update(trans_changes)

        return translations_for_timestamp

    @staticmethod
    def get_lookups_from_enums_module():
        lookups = {}

        for class_name in [obj[0] for obj in inspect.getmembers(enums) if inspect.isclass(obj[1]) and obj[0] != 'AutoNumber']:
            class_obj = getattr(enums, class_name)

            lookup = []
            for name, member in class_obj.__members__.items():
                lookup.append(name)

            lookups[class_name] = lookup

        return lookups

    @staticmethod
    def pretty_print_lookups(lookups):
        parts = []
        for class_name, members in sorted(lookups.items()):
            part = ["    '" + class_name + "': ["]
            for member in members:
                part.append("        '" + member + "',")
            part.append("    ]")
            parts.append('\n'.join(part))

        print('lookups = {')
        print(',\n'.join(parts))
        print('}')


Enums.initialize()


class CommandsToClientTranslator:
    def __init__(self, translations):
        self._commands_to_client = translations.get('CommandsToClient')
        self._errors = translations.get('Errors')

        self._fatal_error = Enums.lookups['CommandsToClient'].index('FatalError')

    def translate(self, commands):
        if self._commands_to_client:
            for command in commands:
                command[0] = self._commands_to_client[command[0]]

        if self._errors:
            for command in commands:
                if command[0] == self._fatal_error:
                    command[1] = self._errors[command[1]]


class LineTypes(enums.AutoNumber):
    connect = ()
    disconnect = ()
    command_to_client = ()
    command_to_server = ()
    game_expired = ()
    log = ()
    blank_line = ()
    ignore = ()


class LogParser:
    def __init__(self, log_timestamp, file):
        self._file = file

        regexes_to_ignore = [
            r'^ ',
            r'^AttributeError:',
            r'^connection_lost$',
            r'^Exception in callback ',
            r'^handle:',
            r'^ImportError:',
            r'^socket\.send\(\) raised exception\.$',
            r'^Traceback \(most recent call last\):',
            r'^UnicodeEncodeError:',
        ]

        self._line_matchers_and_handlers = [
            (LineTypes.command_to_client, re.compile(r'^(?P<client_ids>[\d,]+) <- (?P<commands>.*)'), self._handle_command_to_client),
            (LineTypes.blank_line, re.compile(r'^$'), None),
            (LineTypes.command_to_server, re.compile(r'^(?P<client_id>\d+) -> (?P<command>.*)'), self._handle_command_to_server),
            (LineTypes.log, re.compile(r'^(?P<entry>{.*)'), self._handle_log),
            (LineTypes.connect, re.compile(r'^(?P<client_id>\d+) connect (?P<username>.+) \d+\.\d+\.\d+\.\d+ \S+(?: (?:True|False))?$'), self._handle_connect),
            (LineTypes.disconnect, re.compile(r'^(?P<client_id>\d+) disconnect$'), self._handle_disconnect),
            (LineTypes.game_expired, re.compile(r'^game #(?P<game_id>\d+) expired(?: \(internal #\d+\))?$'), self._handle_game_expired),
            (LineTypes.connect, re.compile(r'^(?P<client_id>\d+) connect \d+\.\d+\.\d+\.\d+ (?P<username>.+)$'), self._handle_connect),
            (LineTypes.disconnect, re.compile(r'^\d+ -> (?P<client_id>\d+) disconnect$'), self._handle_disconnect),  # disconnect after error
            (LineTypes.command_to_server, re.compile(r'^\d+ connect (?P<client_id>\d+) -> (?P<command>.*)'), self._handle_command_to_server),  # command to server after connect printing error
            (LineTypes.ignore, re.compile(r'^connection_made$'), self._handle_connection_made),
            (LineTypes.ignore, re.compile('|'.join(regexes_to_ignore)), None),
        ]

        enums_translations = Enums.get_translations(log_timestamp)
        self._commands_to_client_translator = CommandsToClientTranslator(enums_translations)

        self._connection_made_count = 0

        command_to_client_entry_to_index = {entry: index for index, entry in enumerate(Enums.lookups['CommandsToClient'])}
        self._enum_set_game_board_cell = command_to_client_entry_to_index['SetGameBoardCell']
        self._enum_set_game_player = {index for entry, index in command_to_client_entry_to_index.items() if 'SetGamePlayer' in entry}

    def go(self):
        handled_line_type = None
        line_number = 0
        stop_processing_file = False

        for line in self._file:
            line_number += 1

            if len(line) and line[-1] == '\n':
                line = line[:-1]

            handled_line_type = None
            parse_line_data = None

            for line_type, regex, handler in self._line_matchers_and_handlers:
                match = regex.match(line)
                if match:
                    handled_line_type = line_type
                    if handler:
                        parse_line_data = handler(match)

                        if parse_line_data is None:
                            handled_line_type = None
                            continue
                        elif parse_line_data == 'stop':
                            stop_processing_file = True
                            break
                        else:
                            break
                    else:
                        parse_line_data = ()
                        break

            if stop_processing_file:
                break

            yield (handled_line_type, line_number, line, parse_line_data)

        # make sure last line type is always LineTypes.blank_line
        if handled_line_type != LineTypes.blank_line:
            yield (LineTypes.blank_line, line_number + 1, '', ())

    def _handle_command_to_client(self, match):
        try:
            client_ids = [int(x) for x in match.group('client_ids').split(',')]
            commands = ujson.decode(match.group('commands'))
        except ValueError:
            return

        self._commands_to_client_translator.translate(commands)

        # move SetGamePlayer* commands to the beginning if one of them is after a SetGameBoardCell command
        # reason: need to know what game the client belongs to
        enum_set_game_board_cell_indexes = set()
        enum_set_game_player_indexes = set()
        for index, command in enumerate(commands):
            if command[0] == self._enum_set_game_board_cell:
                enum_set_game_board_cell_indexes.add(index)
            elif command[0] in self._enum_set_game_player:
                enum_set_game_player_indexes.add(index)

        if enum_set_game_board_cell_indexes and enum_set_game_player_indexes and min(enum_set_game_board_cell_indexes) < min(enum_set_game_player_indexes):
            # SetGamePlayer* commands are always right next to each other when there's a SetGameBoardCell command in the batch
            min_index = min(enum_set_game_player_indexes)
            max_index = max(enum_set_game_player_indexes)
            commands = commands[min_index:max_index + 1] + commands[:min_index] + commands[max_index + 1:]

        return client_ids, commands

    def _handle_command_to_server(self, match):
        try:
            client_id = int(match.group('client_id'))
            command = ujson.decode(match.group('command'))
        except ValueError:
            return

        return client_id, command

    def _handle_log(self, match):
        try:
            entry = ujson.decode(match.group('entry'))
        except ValueError:
            return

        return entry,

    def _handle_connect(self, match):
        return int(match.group('client_id')), match.group('username')

    def _handle_disconnect(self, match):
        return int(match.group('client_id')),

    def _handle_game_expired(self, match):
        return int(match.group('game_id')),

    def _handle_connection_made(self, match):
        self._connection_made_count += 1
        if self._connection_made_count == 1:
            return ()
        else:
            return 'stop'


class LogProcessor:
    _game_board_type__nothing = Enums.lookups['GameBoardTypes'].index('Nothing')

    def __init__(self, log_timestamp, file):
        self._log_timestamp = log_timestamp

        self._client_id_to_username = {}
        self._username_to_client_id = {}
        self._client_id_to_game_id = {}
        self._game_id_to_game = {}

        self._log_parser = LogParser(log_timestamp, file)

        self._line_type_to_handler = {
            LineTypes.connect: self._handle_connect,
            LineTypes.disconnect: self._handle_disconnect,
            LineTypes.command_to_client: self._handle_command_to_client,
            LineTypes.command_to_server: self._handle_command_to_server,
            LineTypes.game_expired: self._handle_game_expired,
            LineTypes.log: self._handle_log,
            LineTypes.blank_line: self._handle_blank_line,
        }

        command_to_client_entry_to_index = {entry: index for index, entry in enumerate(Enums.lookups['CommandsToClient'])}
        self._commands_to_client_handlers = {
            # 'FatalError',
            # 'SetClientId',
            # 'SetClientIdToData',
            # 'SetGameState',
            command_to_client_entry_to_index['SetGameBoardCell']: self._handle_command_to_client__set_game_board_cell,
            # 'SetGameBoard',
            command_to_client_entry_to_index['SetScoreSheetCell']: self._handle_command_to_client__set_score_sheet_cell,
            command_to_client_entry_to_index['SetScoreSheet']: self._handle_command_to_client__set_score_sheet,
            command_to_client_entry_to_index['SetGamePlayerJoin']: self._handle_command_to_client__set_game_player_join,
            command_to_client_entry_to_index['SetGamePlayerRejoin']: self._handle_command_to_client__set_game_player_rejoin,
            command_to_client_entry_to_index['SetGamePlayerLeave']: self._handle_command_to_client__set_game_player_leave,
            # 'SetGamePlayerJoinMissing',
            command_to_client_entry_to_index['SetGameWatcherClientId']: self._handle_command_to_client__set_game_watcher_client_id,
            command_to_client_entry_to_index['ReturnWatcherToLobby']: self._handle_command_to_client__return_watcher_to_lobby,
            # 'AddGameHistoryMessage',
            # 'AddGameHistoryMessages',
            # 'SetTurn',
            # 'SetGameAction',
            command_to_client_entry_to_index['SetTile']: self._handle_command_to_client__set_tile,
            # 'SetTileGameBoardType',
            # 'RemoveTile',
            # 'AddGlobalChatMessage',
            # 'AddGameChatMessage',
            # 'DestroyGame',
            # # defunct
            # 'SetGamePlayerUsername',
            command_to_client_entry_to_index['SetGamePlayerClientId']: self._handle_command_to_client__set_game_player_client_id,
        }

        command_to_server_entry_to_index = {entry: index for index, entry in enumerate(Enums.lookups['CommandsToServer'])}
        self._commands_to_server_handlers = {
            # 'CreateGame',
            # 'JoinGame',
            # 'RejoinGame',
            # 'WatchGame',
            # 'LeaveGame',
            command_to_server_entry_to_index['DoGameAction']: self._handle_command_to_server__do_game_action,
            # 'SendGlobalChatMessage',
            # 'SendGameChatMessage',
        }

        self._delayed_calls = []

        self._expired_games = []

    def go(self):
        for line_type, line_number, line, parse_line_data in self._log_parser.go():
            handler = self._line_type_to_handler.get(line_type)
            if handler:
                handler(*parse_line_data)

            if self._expired_games:
                for game in self._expired_games:
                    yield game
                self._expired_games = []

        for game in self._game_id_to_game.values():
            yield game

    def _handle_connect(self, client_id, username):
        self._client_id_to_username[client_id] = username
        self._username_to_client_id[username] = client_id

    def _handle_disconnect(self, client_id):
        self._delayed_calls.append([self._handle_disconnect__delayed, [client_id]])

    def _handle_disconnect__delayed(self, client_id):
        del self._client_id_to_username[client_id]
        self._username_to_client_id = {username: client_id for client_id, username in self._client_id_to_username.items()}

        if len(self._client_id_to_username) != len(self._username_to_client_id):
            print('remove_client: huh?')
            print(self._client_id_to_username)
            print(self._username_to_client_id)

    def _handle_command_to_client(self, client_ids, commands):
        for command in commands:
            try:
                handler = self._commands_to_client_handlers.get(command[0])
                if handler:
                    handler(client_ids, command)
            except:
                traceback.print_exc()

    def _handle_command_to_client__set_game_board_cell(self, client_ids, command):
        client_id, x, y, game_board_type_id = client_ids[0], command[1], command[2], command[3]

        game_id = self._client_id_to_game_id[client_id]
        game = self._game_id_to_game[game_id]

        if game.board[x][y] == LogProcessor._game_board_type__nothing:
            game.played_tiles_order.append((x, y))

        game.board[x][y] = game_board_type_id

    def _handle_command_to_client__set_score_sheet_cell(self, client_ids, command):
        client_id, row, index, value = client_ids[0], command[1], command[2], command[3]

        game_id = self._client_id_to_game_id[client_id]
        game = self._game_id_to_game[game_id]

        if row < 6:
            game.score_sheet_players[row][index] = value
        else:
            game.score_sheet_chain_size[index] = value

    def _handle_command_to_client__set_score_sheet(self, client_ids, command):
        client_id, score_sheet_data = client_ids[0], command[1]

        game_id = self._client_id_to_game_id[client_id]
        game = self._game_id_to_game[game_id]

        game.score_sheet_players[:len(score_sheet_data[0])] = score_sheet_data[0]
        game.score_sheet_chain_size = score_sheet_data[1]

    def _handle_command_to_client__set_game_player_join(self, client_ids, command):
        self._add_client_id_to_game(command[1], command[3])

    def _handle_command_to_client__set_game_player_rejoin(self, client_ids, command):
        self._add_client_id_to_game(command[1], command[3])

    def _handle_command_to_client__set_game_player_leave(self, client_ids, command):
        self._remove_client_id_from_game(command[3])

    def _handle_command_to_client__set_game_watcher_client_id(self, client_ids, command):
        self._add_client_id_to_game(command[1], command[2])

    def _handle_command_to_client__return_watcher_to_lobby(self, client_ids, command):
        self._remove_client_id_from_game(command[2])

    def _handle_command_to_client__set_tile(self, client_ids, command):
        client_id, tile_index, x, y = client_ids[0], command[1], command[2], command[3]

        game_id = self._client_id_to_game_id[client_id]
        game = self._game_id_to_game[game_id]

        player_id = game.username_to_player_id[self._client_id_to_username[client_id]]
        tile = (x, y)

        if game.initial_tile_racks[player_id][tile_index] is None:
            game.tile_rack_tiles.add(tile)
            game.initial_tile_racks[player_id][tile_index] = tile
        elif tile not in game.tile_rack_tiles:
            game.tile_rack_tiles.add(tile)
            game.additional_tile_rack_tiles_order.append(tile)

    def _handle_command_to_client__set_game_player_client_id(self, client_ids, command):
        if command[3] is None:
            self._remove_player_id_from_game(command[1], command[2])
        else:
            self._add_client_id_to_game(command[1], command[3])

    def _add_client_id_to_game(self, game_id, client_id):
        self._client_id_to_game_id[client_id] = game_id

    def _remove_client_id_from_game(self, client_id):
        if client_id in self._client_id_to_game_id:
            del self._client_id_to_game_id[client_id]

    def _remove_player_id_from_game(self, game_id, player_id):
        game = self._game_id_to_game.get(game_id)

        if game:
            client_id = self._username_to_client_id[game.player_id_to_username[player_id]]

            if client_id in self._client_id_to_game_id:
                del self._client_id_to_game_id[client_id]

    def _handle_command_to_server(self, client_id, command):
        try:
            handler = self._commands_to_server_handlers.get(command[0])
            if handler:
                handler(client_id, command)
        except:
            traceback.print_exc()

    def _handle_command_to_server__do_game_action(self, client_id, command):
        game_id = self._client_id_to_game_id.get(client_id)

        if game_id:
            game = self._game_id_to_game[game_id]
            player_id = game.username_to_player_id.get(self._client_id_to_username[client_id])

            if player_id is not None:
                game.actions.append([player_id, command[1:]])

    def _handle_game_expired(self, game_id):
        self._expired_games.append(self._game_id_to_game[game_id])

        del self._game_id_to_game[game_id]

    def _handle_log(self, entry):
        game_id = entry['external-game-id'] if 'external-game-id' in entry else entry['game-id']
        internal_game_id = entry['game-id']

        if game_id in self._game_id_to_game:
            game = self._game_id_to_game[game_id]
        else:
            game = Game(self._log_timestamp, game_id, internal_game_id)
            self._game_id_to_game[game_id] = game

        if entry['_'] == 'game-player':
            player_id = entry['player-id']
            username = entry['username']

            game.player_id_to_username[player_id] = username
            game.username_to_player_id[username] = player_id

            if username not in game.player_join_order:
                game.player_join_order.append(username)
        else:
            if 'state' in entry:
                game.state = entry['state']
            if 'mode' in entry:
                game.mode = entry['mode']
            if 'max-players' in entry:
                game.max_players = entry['max-players']
            if 'begin' in entry:
                game.begin = entry['begin']
            if 'end' in entry:
                game.end = entry['end']
            if 'score' in entry:
                game.score = entry['score']
            if 'scores' in entry:
                game.score = entry['scores']

    def _handle_blank_line(self):
        if self._delayed_calls:
            for func, args in self._delayed_calls:
                func(*args)
            del self._delayed_calls[:]


class Game:
    _game_board_type__nothing = Enums.lookups['GameBoardTypes'].index('Nothing')
    _score_sheet_indexes__client = Enums.lookups['ScoreSheetIndexes'].index('Client')

    def __init__(self, log_timestamp, game_id, internal_game_id):
        self.log_timestamp = log_timestamp
        self.game_id = game_id
        self.internal_game_id = internal_game_id
        self.state = None
        self.mode = None
        self.max_players = None
        self.begin = None
        self.end = None
        self.score = None
        self.player_id_to_username = {}
        self.username_to_player_id = {}
        self.player_join_order = []
        self.board = [[Game._game_board_type__nothing for y in range(9)] for x in range(12)]
        self.score_sheet_players = [[0, 0, 0, 0, 0, 0, 0, 60] for x in range(6)]
        self.score_sheet_chain_size = [0, 0, 0, 0, 0, 0, 0]
        self.played_tiles_order = []
        self.tile_rack_tiles = set()
        self.initial_tile_racks = [[None, None, None, None, None, None] for x in range(6)]
        self.additional_tile_rack_tiles_order = []
        self.actions = []

    def get_server_game(self):
        num_players = len(self.player_id_to_username)

        position_tiles = self.played_tiles_order[:num_players]
        initial_tile_rack_tiles = [tile for tile_rack in self.initial_tile_racks[:num_players] for tile in tile_rack if tile is not None]
        remaining_tiles = list({(x, y) for x in range(12) for y in range(9)} - set(position_tiles) - self.tile_rack_tiles)
        random.shuffle(remaining_tiles)
        tile_bag = position_tiles + initial_tile_rack_tiles + self.additional_tile_rack_tiles_order + remaining_tiles
        tile_bag.reverse()

        server_game = server.Game(self.game_id, self.internal_game_id, Enums.lookups['GameModes'].index(self.mode), self.max_players, Game._add_pending_messages, False, tile_bag)

        player_id_to_client = [Client(player_id, username) for player_id, username in sorted(self.player_id_to_username.items())]

        for username in self.player_join_order:
            client = player_id_to_client[self.username_to_player_id[username]]
            server_game.join_game(client)

        for player_id, action in self.actions:
            game_action_id = action[0]
            data = action[1:]
            server_game.do_game_action(player_id_to_client[player_id], game_action_id, data)

        return server_game

    def is_identical(self, server_game):
        num_players = len(self.player_id_to_username)
        has_identical_board = str(self.board) == str(server_game.game_board.x_to_y_to_board_type)
        has_identical_score_sheet_players = str(self.score_sheet_players[:num_players]) == str([x[:8] for x in server_game.score_sheet.player_data])
        has_identical_score_sheet_chain_size = str(self.score_sheet_chain_size) == str(server_game.score_sheet.chain_size)

        return has_identical_board and has_identical_score_sheet_players and has_identical_score_sheet_chain_size

    def make_game_file(self, server_game):
        num_tiles_on_board = len([1 for row in self.board for cell in row if cell != Game._game_board_type__nothing])

        game_data = {}

        game_data['game_id'] = server_game.game_id
        game_data['internal_game_id'] = server_game.internal_game_id
        game_data['state'] = server_game.state
        game_data['mode'] = server_game.mode
        game_data['max_players'] = server_game.max_players
        game_data['num_players'] = server_game.num_players
        game_data['tile_bag'] = server_game.tile_bag
        game_data['turn_player_id'] = server_game.turn_player_id
        game_data['turns_without_played_tiles_count'] = server_game.turns_without_played_tiles_count
        game_data['history_messages'] = server_game.history_messages

        # game_data['add_pending_messages'] -- exclude
        # game_data['logging_enabled'] -- exclude
        # game_data['client_ids'] -- exclude
        # game_data['watcher_client_ids'] -- exclude
        # game_data['expiration_time'] -- exclude

        game_data['game_board'] = server_game.game_board.x_to_y_to_board_type

        score_sheet = server_game.score_sheet
        game_data['score_sheet'] = {
            'player_data': [row[:Game._score_sheet_indexes__client] + [None] for row in score_sheet.player_data],
            'available': score_sheet.available,
            'chain_size': score_sheet.chain_size,
            'price': score_sheet.price,
            'creator_username': score_sheet.creator_username,
            'username_to_player_id': score_sheet.username_to_player_id,
        }

        game_data['tile_racks'] = server_game.tile_racks.racks if server_game.tile_racks else None

        game_data_actions = []
        for action in server_game.actions:
            game_data_action = dict(action.__dict__)
            game_data_action['__name__'] = action.__class__.__name__
            del game_data_action['game']
            game_data_actions.append(game_data_action)
        game_data['actions'] = game_data_actions

        filename = '%d_%05d_%03d.bin' % (self.log_timestamp, self.internal_game_id, num_tiles_on_board)
        with open('/opt/data/tim/' + filename, 'wb') as f:
            pickle.dump(game_data, f)

        return filename

    @staticmethod
    def _add_pending_messages(messages, client_ids=None):
        pass


class Client:
    def __init__(self, player_id, username):
        self.client_id = player_id + 1
        self.username = username
        self.game_id = None
        self.player_id = None


class IndividualGameLogMaker:
    def __init__(self, log_timestamp, file):
        self._log_timestamp = log_timestamp

        self._client_id_to_username = {}
        self._username_to_client_id = {}
        self._client_id_to_game_id = {}

        self._log_parser = LogParser(log_timestamp, file)

        self._line_type_to_handler = {
            LineTypes.connect: self._handle_connect,
            LineTypes.disconnect: self._handle_disconnect,
            LineTypes.command_to_client: self._handle_command_to_client,
            LineTypes.command_to_server: self._handle_command_to_server,
            LineTypes.game_expired: self._handle_game_expired,
            LineTypes.log: self._handle_log,
            LineTypes.blank_line: self._handle_blank_line,
        }

        command_to_client_entry_to_index = {entry: index for index, entry in enumerate(Enums.lookups['CommandsToClient'])}
        self._commands_to_client_handlers = {
            # 'FatalError',
            # 'SetClientId',
            # 'SetClientIdToData',
            # 'SetGameState',
            command_to_client_entry_to_index['SetGameBoardCell']: self._handle_command_to_client__set_game_board_cell,
            # 'SetGameBoard',
            command_to_client_entry_to_index['SetScoreSheetCell']: self._handle_command_to_client__set_score_sheet_cell,
            command_to_client_entry_to_index['SetScoreSheet']: self._handle_command_to_client__set_score_sheet,
            command_to_client_entry_to_index['SetGamePlayerJoin']: self._handle_command_to_client__set_game_player_join,
            command_to_client_entry_to_index['SetGamePlayerRejoin']: self._handle_command_to_client__set_game_player_rejoin,
            command_to_client_entry_to_index['SetGamePlayerLeave']: self._handle_command_to_client__set_game_player_leave,
            # 'SetGamePlayerJoinMissing',
            command_to_client_entry_to_index['SetGameWatcherClientId']: self._handle_command_to_client__set_game_watcher_client_id,
            command_to_client_entry_to_index['ReturnWatcherToLobby']: self._handle_command_to_client__return_watcher_to_lobby,
            # 'AddGameHistoryMessage',
            # 'AddGameHistoryMessages',
            # 'SetTurn',
            # 'SetGameAction',
            command_to_client_entry_to_index['SetTile']: self._handle_command_to_client__set_tile,
            # 'SetTileGameBoardType',
            # 'RemoveTile',
            # 'AddGlobalChatMessage',
            # 'AddGameChatMessage',
            # 'DestroyGame',
            # # defunct
            # 'SetGamePlayerUsername',
            command_to_client_entry_to_index['SetGamePlayerClientId']: self._handle_command_to_client__set_game_player_client_id,
        }

        command_to_server_entry_to_index = {entry: index for index, entry in enumerate(Enums.lookups['CommandsToServer'])}
        self._commands_to_server_handlers = {
            # 'CreateGame',
            # 'JoinGame',
            # 'RejoinGame',
            # 'WatchGame',
            # 'LeaveGame',
            command_to_server_entry_to_index['DoGameAction']: self._handle_command_to_server__do_game_action,
            # 'SendGlobalChatMessage',
            # 'SendGameChatMessage',
        }

        self._delayed_calls = []

        self._line_number = 1
        self._batch_line_number = 1
        self._batch = []

        self._game_id_to_game_log = {}
        self._batch_add_client_id = None
        self._batch_remove_client_id = None
        self._batch_game_id = None
        self._batch_game_client_ids = []
        self._batch_destroy_game_ids = []
        self._client_id_to_add_batch = {}
        self._re_disconnect = re.compile(r'^\d+ disconnect$')

    def go(self):
        for line_type, line_number, line, parse_line_data in self._log_parser.go():
            self._batch.append(line)

            handler = self._line_type_to_handler.get(line_type)
            if handler:
                self._line_number = line_number
                handler(*parse_line_data)

        game_ids = list(self._game_id_to_game_log.keys())
        for game_id in game_ids:
            self._handle_game_expired(game_id)
        self._batch_destroy_game_ids = game_ids
        self._batch_completed(None, None)

    def _handle_connect(self, client_id, username):
        if self._client_id_to_username.get(client_id) != username:
            self._batch_add_client_id = client_id

        self._client_id_to_username[client_id] = username
        self._username_to_client_id[username] = client_id

    def _handle_disconnect(self, client_id):
        self._delayed_calls.append([self._handle_disconnect__delayed, [client_id]])

    def _handle_disconnect__delayed(self, client_id):
        if self._client_id_to_username.get(client_id):
            self._batch_remove_client_id = client_id

        del self._client_id_to_username[client_id]
        self._username_to_client_id = {username: client_id for client_id, username in self._client_id_to_username.items()}

        if len(self._client_id_to_username) != len(self._username_to_client_id):
            print('remove_client: huh?')
            print(self._client_id_to_username)
            print(self._username_to_client_id)

    def _handle_command_to_client(self, client_ids, commands):
        for command in commands:
            try:
                handler = self._commands_to_client_handlers.get(command[0])
                if handler:
                    handler(client_ids, command)
            except:
                traceback.print_exc()

    def _handle_command_to_client__set_game_board_cell(self, client_ids, command):
        self._batch_game_id = self._client_id_to_game_id[client_ids[0]]

    def _handle_command_to_client__set_score_sheet_cell(self, client_ids, command):
        self._batch_game_id = self._client_id_to_game_id[client_ids[0]]

    def _handle_command_to_client__set_score_sheet(self, client_ids, command):
        self._batch_game_id = self._client_id_to_game_id[client_ids[0]]

    def _handle_command_to_client__set_game_player_join(self, client_ids, command):
        self._add_client_id_to_game(command[1], command[3])

    def _handle_command_to_client__set_game_player_rejoin(self, client_ids, command):
        self._add_client_id_to_game(command[1], command[3])

    def _handle_command_to_client__set_game_player_leave(self, client_ids, command):
        self._remove_client_id_from_game(command[3])

    def _handle_command_to_client__set_game_watcher_client_id(self, client_ids, command):
        self._add_client_id_to_game(command[1], command[2])

    def _handle_command_to_client__return_watcher_to_lobby(self, client_ids, command):
        self._remove_client_id_from_game(command[2])

    def _handle_command_to_client__set_tile(self, client_ids, command):
        self._batch_game_id = self._client_id_to_game_id[client_ids[0]]

    def _handle_command_to_client__set_game_player_client_id(self, client_ids, command):
        if command[3] is None:
            self._remove_player_id_from_game(command[1], command[2])
        else:
            self._add_client_id_to_game(command[1], command[3])

    def _add_client_id_to_game(self, game_id, client_id):
        self._client_id_to_game_id[client_id] = game_id

        self._batch_game_id = game_id

    def _remove_client_id_from_game(self, client_id):
        if client_id in self._client_id_to_game_id:
            self._batch_game_id = self._client_id_to_game_id[client_id]

            del self._client_id_to_game_id[client_id]

    def _remove_player_id_from_game(self, game_id, player_id):
        client_id = self._username_to_client_id[self._game_id_to_game_log[game_id].player_id_to_username[player_id]]

        if client_id in self._client_id_to_game_id:
            self._batch_game_id = game_id

            del self._client_id_to_game_id[client_id]

    def _handle_command_to_server(self, client_id, command):
        try:
            handler = self._commands_to_server_handlers.get(command[0])
            if handler:
                handler(client_id, command)
        except:
            traceback.print_exc()

    def _handle_command_to_server__do_game_action(self, client_id, command):
        game_id = self._client_id_to_game_id.get(client_id)

        if game_id:
            game_log = self._game_id_to_game_log[game_id]
            player_id = game_log.username_to_player_id.get(self._client_id_to_username[client_id])

            if player_id is not None:
                self._batch_game_id = game_id

    def _handle_game_expired(self, game_id):
        self._batch_destroy_game_ids.append(game_id)

    def _handle_log(self, entry):
        game_id = entry['external-game-id'] if 'external-game-id' in entry else entry['game-id']
        internal_game_id = entry['game-id']

        if game_id in self._game_id_to_game_log:
            game_log = self._game_id_to_game_log[game_id]
        else:
            game_log = IndividualGameLog(self._log_timestamp, internal_game_id)
            self._game_id_to_game_log[game_id] = game_log

            for client_id, add_batch in self._client_id_to_add_batch.items():
                batch_line_number, batch = add_batch
                batch = [line for line in batch if not self._re_disconnect.match(line)]
                game_log.line_number_to_batch[batch_line_number] = batch

        if entry['_'] == 'game-player':
            player_id = entry['player-id']
            username = entry['username']

            game_log.player_id_to_username[player_id] = username
            game_log.username_to_player_id[username] = player_id

    def _handle_blank_line(self):
        if self._delayed_calls:
            for func, args in self._delayed_calls:
                func(*args)
            del self._delayed_calls[:]

        self._batch_completed(self._batch_line_number, self._batch)
        self._batch_line_number = self._line_number + 1
        self._batch = []

    def _batch_completed(self, batch_line_number, batch):
        if self._batch_add_client_id:
            for game_log in self._game_id_to_game_log.values():
                game_log.line_number_to_batch[batch_line_number] = batch

            self._client_id_to_add_batch[self._batch_add_client_id] = [batch_line_number, batch]
            self._batch_add_client_id = None

        if self._batch_remove_client_id:
            for game_log in self._game_id_to_game_log.values():
                game_log.line_number_to_batch[batch_line_number] = batch

            del self._client_id_to_add_batch[self._batch_remove_client_id]
            self._batch_remove_client_id = None

        if self._batch_game_id:
            game_log = self._game_id_to_game_log[self._batch_game_id]
            game_log.line_number_to_batch[batch_line_number] = batch

            self._batch_game_id = None

        if self._batch_destroy_game_ids:
            for game_id in self._batch_destroy_game_ids:
                game_log = self._game_id_to_game_log[game_id]
                game_log.output()
                del self._game_id_to_game_log[game_id]
            self._batch_destroy_game_ids = []


class IndividualGameLog:
    def __init__(self, log_timestamp, internal_game_id):
        self.log_timestamp = log_timestamp
        self.internal_game_id = internal_game_id

        self.player_id_to_username = {}
        self.username_to_player_id = {}

        self.line_number_to_batch = {}

    def output(self):
        filename = '%d_%05d.txt' % (self.log_timestamp, self.internal_game_id)
        with open('/opt/data/tim/' + filename, 'w') as f:
            for line_number, batch in sorted(self.line_number_to_batch.items()):
                f.write('--- batch line number: ' + str(line_number) + '\n')
                f.write('\n'.join(batch))
                f.write('\n')


def main():
    for timestamp, path in util.get_log_file_paths('py', begin=1408905413):
        print(path)

        with util.open_possibly_gzipped_file(path) as file:
            log_processor = LogProcessor(timestamp, file)

            for game in log_processor.go():
                server_game = game.get_server_game()

                messages = [game.log_timestamp, game.internal_game_id]
                if game.is_identical(server_game):
                    messages.append('yay!')
                    if server_game.state == Enums.lookups['GameStates'].index('InProgress') and len(game.player_id_to_username) > 1:
                        filename = game.make_game_file(server_game)
                        messages.append(filename)
                else:
                    messages.append('boo!')

                print(*messages)


if __name__ == '__main__':
    main()
    # Enums.pretty_print_lookups(Enums.get_lookups_from_enums_module())