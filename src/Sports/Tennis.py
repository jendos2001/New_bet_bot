from copy import deepcopy
from src.Sports.Sport import Sport


class Tennis(Sport):

    def __init__(self):
        super().__init__("2")

    def _make_matches(self, tournaments):
        for item in tournaments:
            for elem in self._tournaments.values():
                if item['TEMPLATE_ID'] in elem.values():
                    matches = {}
                    for event in item['EVENTS']:
                        if event['STAGE'] != 'INTERRUPTED' and event['STAGE'] != 'CANCELED':
                            matches[event['SHORTNAME_AWAY'] + ' - ' + event['SHORTNAME_HOME']] = \
                                {'match_id': event['EVENT_ID'],
                                 'teams': f"{event['HOME_NAME']} - {event['AWAY_NAME']}"}
                            if 'ROUND' in event.keys():
                                matches[event['SHORTNAME_AWAY'] + ' - ' + event['SHORTNAME_HOME']]['round'] \
                                    = event['ROUND']
                    self._tennis_matches[item['NAME_PART_2']] = matches
                    self._check_id[item['NAME_PART_2']] = item['TOURNAMENT_STAGE_ID']
                    self.__remaining_matches = deepcopy(self._tennis_matches.copy())
