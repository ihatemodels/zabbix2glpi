import argparse
from glpi import Glpi
from zabbix import Zabbix


def main():

    parser = argparse.ArgumentParser(
        description="Open glpi tickets based on zabbix events"
    )

    parser.add_argument(
        '--hostname',
        '-host',
        dest='hostname',
        type=str,
        help='Zabbix hostname Macro: {HOST.NAME}',
        required=True
    )

    parser.add_argument(
        '--eventid',
        '-eid',
        dest='eventid',
        type=int,
        help='Zabbix event-id, Macro: {EVENT.ID}',
        required=True
    )

    parser.add_argument(
        '--triggerid',
        '-tid',
        dest='triggerid',
        type=int,
        help='Zabbix trigger-id, Macro: {TRIGGER.ID}',
        required=True
    )

    parser.add_argument(
        '--ticketname',
        '-tn',
        dest='ticketname',
        type=str,
        help='GLPI Ticket name, Zabbix Macro: {TRIGGER.NAME}',
        required=True
    )

    parser.add_argument(
        '--ticketuser',
        '-user',
        dest='ticketuser',
        type=str,
        help='Assign the ticket to specific GLPI user',
    )

    args = parser.parse_args()

    glpi = Glpi(user="user", password="password",
                app_token="your_glpi_user_token",
                url="http://your_glpi_address")

    glpi.create_ticket(args.hostname, args.eventid,
                       args.triggerid, args.ticketname, urgency=4)

    # This method is responsible to assign the ticket to specific user.
    glpi.assign_ticket("GLPI_username", glpi.last_created_ticket_id)

    zabbix = Zabbix(user='user',
                    password='password',
                    url='http://your_zabbix_address')

    # The method acknowledge the event in Zabbix, remove if you dont want to.
    zabbix.ack_event(glpi_ticket=glpi.last_created_ticket_id,
                     event_id=args.eventid)

    glpi.kill_session()


if __name__ == "__main__":
    main()
