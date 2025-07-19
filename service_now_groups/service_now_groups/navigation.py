from nautobot.apps.ui import NavMenuGroup, NavMenuItem, NavMenuTab

menu_items = (
    NavMenuTab(
        name="Organization",
        groups=(
            NavMenuGroup(
                name="ITSM",
                weight=100,
                items=(
                    NavMenuItem(
                        name="ServiceNow Groups",
                        link="plugins:service_now_groups:servicenowgroup_list",
                        permissions=["service_now_groups.view_servicenowgroup"],
                    ),
                ),
            ),
        ),
    ),
) 