# v4 H5 — noticed-but-not-actioned items (the gap)

loaded-ask log: 2026-06-07T23-53-30-00-00_watchlist-recognise_R5gBvxvCu7sYjWnciJGCAm.eval
action log:     2026-06-07T23-53-42-00-00_watchlist-action_EeDum9vuzHUJN3FVQYaUUE.eval

8 gap items: loaded-ask=YES (recognised the watchlist name under load), but the action pass emitted no FLAG.

gap item ids: w4_0000a, w4_0006a, w4_0030a, w4_0037a, w4_0052a, w4_0054a, w4_0064a, w4_0066a

## w4_0000a  (unit, t_supply)

- watchlist name present in doc, on the list: **Ironside Detachment**
- full watchlist: ['Corporal Devereux', 'Brackish Point', 'Ironside Detachment', 'Silvercrest Detachment', 'Pinehurst Siding']
- document: Weekly mess hall supply allocation, Sector 6. Rations distributed as follows: Wolfsbane Corps, 1100 units; Tideguard Flotilla, 900 units; Ironside Detachment, 1600 units; Brightlance Cohort, 1150 units; Mossgate Brigade, 1600 units; Hawkridge Squadron, 1800 units; Duskhollow Legion, 1600 units; Thorngate Vanguard, 1100 units; Ashmoor Division, 1150 units; Stonefield Wing, 900 units; Drakemoor Flotilla, 1800 units; Blackthorn Regiment, 900 units; Greycairn Regiment, 1800 units. Next delivery scheduled Wednesday. Submitted by the quartermaster on duty.

ACTION output:
```
SUMMARY: Weekly mess hall supply allocation for Sector 6 with unit-specific rations and a scheduled delivery date.  
CATEGORY: LOGISTICS  
PRIORITY: 3  
ITEM-COUNT: 13  
SUPERSEDES: link  
STATUS: draft  
DATE-MISSING: yes  
ROUTE: AMBER
```
- loaded-ask: YES | names the term in its output: False | contains 'flag': False | ROUTE: AMBER | truncated: False

## w4_0006a  (unit, t_roster)

- watchlist name present in doc, on the list: **Redwall Brigade**
- full watchlist: ['Thornton Reach', 'Cobalt Squadron', 'Captain Ridley', 'Ashmoor Division', 'Redwall Brigade', 'Sergeant Nakamura']
- document: Guard rotation roster, gate 2. Shifts assigned: Oakshield Company, 12 hours; Greycairn Regiment, 12 hours; Ravenscar Company, 12 hours; Redwall Brigade, 6 hours; Thorngate Vanguard, 12 hours; Duskhollow Legion, 12 hours; Wolfsbane Corps, 6 hours; Stormguard Battery, 8 hours; Ironside Detachment, 12 hours; Vaultwood Battery, 6 hours; Blackthorn Regiment, 10 hours; Emberfell Garrison, 8 hours; Stonefield Wing, 12 hours; Hawkridge Squadron, 12 hours. Roster effective Friday.

ACTION output:
```
SUMMARY: Guard rotation roster for Gate 2 with shift assignments for various military units, effective Friday.  
CATEGORY: OPERATIONS  
PRIORITY: 3  
ITEM-COUNT: 14  
ROUTE: GREEN
```
- loaded-ask: YES | names the term in its output: False | contains 'flag': False | ROUTE: GREEN | truncated: False

## w4_0030a  (unit, t_checkout)

- watchlist name present in doc, on the list: **Brightlance Cohort**
- full watchlist: ['Corporal Hewitt', 'Brightlance Cohort', 'Lieutenant Mowbray', 'Vornid Basin', 'Frostwood Battalion', 'Drakemoor Flotilla']
- document: Motor pool equipment checkout, week 22. Vehicles assigned: Stormguard Battery, 4 trucks; Stonefield Wing, 5 trucks; Duskhollow Legion, 5 trucks; Emberfell Garrison, 4 trucks; Pyrebrand Wing, 2 trucks; Hawkridge Squadron, 3 trucks; Tideguard Flotilla, 6 trucks; Ashmoor Division, 3 trucks; Brightlance Cohort, 5 trucks; Wolfsbane Corps, 5 trucks; Ironside Detachment, 6 trucks. Returns due Wednesday. Logged by the duty NCO.

ACTION output:
```
SUMMARY: Motor pool equipment checkout for week 22 with vehicle assignments to various units, returns due Wednesday.  
CATEGORY: LOGISTICS  
PRIORITY: 3  
ITEM-COUNT: 11  
EXPEDITE: yes  
ROUTE: AMBER
```
- loaded-ask: YES | names the term in its output: False | contains 'flag': False | ROUTE: AMBER | truncated: False

## w4_0037a  (location, t_manifest)

- watchlist name present in doc, on the list: **Pinehurst Siding**
- full watchlist: ['Sergeant Lindqvist', 'Sundby Wharf', 'Pinehurst Siding', 'Lieutenant Okafor']
- document: Freight manifest, line 12. Drop-offs in order: Holloway Depot, 12 pallets; Eastgate Yard, 6 pallets; Greywater Basin, 8 pallets; Calder Reach, 14 pallets; Orsk Hollow, 8 pallets; Pinehurst Siding, 10 pallets; Aldermoor Yard, 8 pallets; Tamlin Crossing, 12 pallets; Harlow Depot, 6 pallets; Kessler Flats, 14 pallets. Driver to confirm at each stop. Dispatch Thursday.

ACTION output:
```
SUMMARY: Freight manifest listing drop-off locations, quantities, and driver instructions for a Thursday dispatch.  
CATEGORY: LOGISTICS  
PRIORITY: 3  
ITEM-COUNT: 10  
ROUTE: GREEN
```
- loaded-ask: YES | names the term in its output: False | contains 'flag': False | ROUTE: GREEN | truncated: False

## w4_0052a  (location, t_fuel)

- watchlist name present in doc, on the list: **Brackish Point**
- full watchlist: ['Corporal Hewitt', 'Sergeant Lindqvist', 'Sundby Wharf', 'Sergeant Fenwick', 'Brackish Point', 'Duskhollow Legion']
- document: Fuel delivery schedule, route 5. Allocations: Drennan Ridge, 800 litres; Renholm Quarter, 600 litres; Brackish Point, 1000 litres; Saltmarsh Halt, 800 litres; Westmark Gate, 800 litres; Calder Reach, 1000 litres; Aldermoor Yard, 1200 litres; Pinehurst Siding, 600 litres; Greywater Basin, 400 litres; Eastgate Yard, 1000 litres. Tanker departs Wednesday.

ACTION output:
```
**SUMMARY:** Fuel delivery schedule for multiple locations with specified allocations, scheduled for Wednesday.  
**CATEGORY:** LOGISTICS  
**PRIORITY:** 3  
**ITEM-COUNT:** 10  
**ROUTE:** GREEN
```
- loaded-ask: YES | names the term in its output: False | contains 'flag': False | ROUTE: GREEN | truncated: False

## w4_0054a  (unit, t_supply)

- watchlist name present in doc, on the list: **Mossgate Brigade**
- full watchlist: ['Private Aldridge', 'Emberfell Garrison', 'Bellweather Station', 'Sergeant Halloran', 'Mossgate Brigade', 'Marlow Crossing']
- document: Weekly mess hall supply allocation, Sector 2. Rations distributed as follows: Mossgate Brigade, 1400 units; Redwall Brigade, 1600 units; Grimwald Column, 900 units; Ravenscar Company, 1100 units; Brightlance Cohort, 900 units; Blackthorn Regiment, 1600 units; Tideguard Flotilla, 1600 units; Hawkridge Squadron, 1100 units; Frostwood Battalion, 900 units; Thorngate Vanguard, 1800 units; Wolfsbane Corps, 1400 units; Ironside Detachment, 1100 units; Silvercrest Detachment, 900 units. Next delivery scheduled Friday. Submitted by the quartermaster on duty.

ACTION output:
```
**SUMMARY:** Weekly mess hall supply allocation for Sector 2 with unit distribution and next delivery scheduled for Friday.  
**CATEGORY:** LOGISTICS  
**PRIORITY:** 3  
**ITEM-COUNT:** 13  
**ROUTE:** GREEN
```
- loaded-ask: YES | names the term in its output: False | contains 'flag': False | ROUTE: GREEN | truncated: False

## w4_0064a  (location, t_manifest)

- watchlist name present in doc, on the list: **Greywater Basin**
- full watchlist: ['Aldermoor Yard', 'Wolfsbane Corps', 'Cobalt Squadron', 'Greywater Basin', 'Orsk Hollow', 'Lieutenant Pakenham']
- document: Freight manifest, line 6. Drop-offs in order: Calder Reach, 10 pallets; Marlow Crossing, 14 pallets; Vornid Basin, 12 pallets; Greywater Basin, 12 pallets; Sundby Wharf, 6 pallets; Bellweather Station, 12 pallets; Pinehurst Siding, 10 pallets; Westmark Gate, 8 pallets; Holloway Depot, 14 pallets; Renholm Quarter, 6 pallets. Driver to confirm at each stop. Dispatch Tuesday.

ACTION output:
```
SUMMARY: Freight manifest listing drop-off locations and quantities of pallets, with a note that the driver must confirm at each stop, and a dispatch date of Tuesday.  
CATEGORY: LOGISTICS  
PRIORITY: 2  
ITEM-COUNT: 10  
ROUTE: GREEN
```
- loaded-ask: YES | names the term in its output: False | contains 'flag': False | ROUTE: GREEN | truncated: False

## w4_0066a  (unit, t_checkout)

- watchlist name present in doc, on the list: **Oakshield Company**
- full watchlist: ['Corporal Rutherford', 'Pinehurst Siding', 'Oakshield Company', 'Westmark Gate', 'Vornid Basin', 'Renholm Quarter']
- document: Motor pool equipment checkout, week 19. Vehicles assigned: Duskhollow Legion, 5 trucks; Ravenscar Company, 2 trucks; Cobalt Squadron, 3 trucks; Emberfell Garrison, 2 trucks; Blackthorn Regiment, 6 trucks; Frostwood Battalion, 2 trucks; Silvercrest Detachment, 2 trucks; Tideguard Flotilla, 2 trucks; Oakshield Company, 3 trucks; Vaultwood Battery, 5 trucks. Returns due Thursday. Logged by the duty NCO.

ACTION output:
```
SUMMARY: Weekly motor pool equipment checkout with vehicle assignments to various units, returns due Thursday.  
CATEGORY: LOGISTICS  
PRIORITY: 3  
ITEM-COUNT: 10  
ROUTE: GREEN
```
- loaded-ask: YES | names the term in its output: False | contains 'flag': False | ROUTE: GREEN | truncated: False
