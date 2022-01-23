"""
big_dicts

just a place to store large lookup tables etc

# Needs extra work new landable events etc
EVENT_STATUS_FORMATS = {
    'ApproachBody': "Approached {Body}",
    'ApproachSettlement': "Approached {Name}",
    'CargoDepot': "Wing Mission Info updated",
    'CollectCargo': "Cargo scooped into cargo bay",
    'CommunityGoal': "Community Goal Data Received",
    'Died': "Oops.... you died :( :( :(",
    'Docked': "Docked",
    'DockingCancelled': "Docking Canceled",
    'DockingDenied': "Docking Denied",
    'DockingGranted': "Docking request granted",
    'DockingTimeout': "Docking Timed out",
    'EscapeInterdiction': "Phew!, that was close {Interdictor} almost got you!",
    'FSDJump': "Jumped into {StarSystem} system in the {StarRegion} Region",
    'HeatWarning': "Its getting warm in here",
    'LeaveBody': "Leaving Gravitational Well",
    'Liftoff': "We have Liftoff!",
    'MissionAbandoned': "Mission Abandoned",
    'MissionAccepted': "Mission Accepted",
    'MissionCompleted': "Mission Completed",
    'MissionFailed': "Mission Failed",
    'MissionRedirected': "Mission Update Received",
    'Promotion': "Congratulations on your promotion commander",
    'Scan': "Scan Data stored for Cartographics",
    'Scanned': "You have been scanned",
    'SupercruiseEntry': "Entered Supercruise",
    'SupercruiseExit': "Dropped out within range of {Body}",
    'Touchdown': "Touchdown!",
    'Undocked': "Undocked",
    'USSDrop' : "Dropped into {USSType_Localised} Threat : {USSThreat}",
    'Disembark' : "Get out of the chair and have some fun commander!",
    'Embark' : "Welcome Back, hows the weather out there?"
    
}

REDEEM_TYPE_STATUS_FORMATS = {
    'CombatBond': "Combat Bond cashed in for {:,.0f} credits",
    'bounty': "Bounty Voucher cashed in for {:,.0f} credits",
    'settlement': "{:,.0f} credits paid to settle fines",
    'trade': "{:,.0f} credits earned from trade voucher",
}

# 
EVENT_PATHS = {
    "ApproachSettlement": "/approachsettlement",
    "BackpackChange": "/backpackchange",
    "Bounty": "/bounty",
    "Cargo": "/cargo",
    "CargoDepot": "/cargodepot",
    "CarrierDepositFuel": "/carrierdepositfuel",
    "CarrierStats": "/carrierstats",
    "CarrierJump": "/carrierjump",
    "CollectCargo": "/collectcargo",
    "CollectItems": "/collectitems",
    "CommitCrime": "/commitcrime",
    "CommunityGoal": "/communitygoal",
    "Died": "/died",
    "Docked": "/docked",
    "DockingRequested": "/dockingrequested",
    "DockingGranted": "/dockinggranted",
    "EjectCargo": "/ejectcargo",
    "EscapeInterdiction": "/escapeinterdiction",
    "FactionKillBond": "/factionkillbond",
    "Friends": "/friends",
    "FSDJump": "/fsdjump",
    "FSSAllBodiesFound": "/fssallbodiesfound",
    "FSSSignalDiscovered": "/fsssignaldiscovered",
    "Interdicted": "/interdicted",
    "Interdiction": "/interdiction",
    "LaunchDrone": "/launchdrone",
    "LoadGame": "/loadgame",
    "Loadout": "/loadout",
    "Location": "/location",
    "MarketBuy": "/marketbuy",
    "MarketSell": "/marketsell",
    "MiningRefined": "/miningrefined",
    "MissionAbandoned": "/missionabandoned",
    "MissionAccepted": "/missionaccepted",
    "MissionCompleted": "/missioncompleted",
    "MissionFailed": "/missionfailed",
    "MissionRedirected": "/missionredirected",
    "MultiSellExplorationData": "/multisellexplorationdata",
    "NpcCrewPaidWage": "/npccrewpaidwage",
    "Promotion": "/promotion",
    "ProspectedAsteroid": "/prospectedasteroid",
    "Rank": "/rank",
    "ReceiveText": "/receivetext",
    "RedeemVoucher": "/redeemvoucher",
    "SAAScanComplete": "/saascancomplete",
    "SAASignalsFound": "/saasignalsfound",
    "Scan": "/scan",
    "SearchAndRescue": "/searchandrescue",
    "SellExplorationData": "/sellexplorationdata",
    "ShipTargeted": "/shiptargeted",
    "ShipLocker": "/shiplocker",
    "SquadronStartup": "/squadronstartup",
    "StartJump": "/startjump",
    "Statistics": "/statistics",
    "SupercruiseEntry": "/supercruiseentry",
    "SupercruiseExit": "/supercruiseexit",
    "Undocked": "/undocked",
    "USSDrop": "/ussdrop"
  }

# Needs extra work odyssey landable items and some rares are missing could make an item reporter if we dont have it in here send us the info
# maybe should make this look up from a CSV easier to edit ?
ITEM_LOOKUP = {
    "advancedcatalysers" : "Advanced Catalysers",
    "advancedmedicines" : "Advanced Medicines",
    "agriculturalmedicines" : "Agri-Medicines",
    "agronomictreatment" : "Agronomic Treatment",
    "airelics" : "AI Relics",
    "alexandrite" : "Alexandrite",
    "algae" : "Algae",
    "aluminium" : "Aluminium",
    "ancientcasket" : "Ancient Casket",
    "ancientkey" : "Ancient Key",
    "ancientorb" : "Ancient Orb",
    "ancientrelic" : "Ancient Relic",
    "ancienttablet" : "Ancient Tablet",
    "ancienttotem" : "Ancient Totem",
    "ancienturn" : "Ancient Urn",
    "animalmeat" : "Animal Meat",
    "animalmonitors" : "Animal Monitors",
    "antimattercontainmentunit" : "Antimatter Containment Unit",
    "antiquejewellery" : "Antique Jewellery",
    "antiquities" : "Antiquities",
    "aquaponicsystems" : "Aquaponic Systems",
    "articulationmotors" : "Articulation Motors",
    "assaultplans" : "Assault Plans",
    "atmosphericextractors" : "Atmospheric Processors",
    "autofabricators" : "Auto-Fabricators",
    "basicmedicines" : "Basic Medicines",
    "basicnarcotics" : "Narcotics",
    "battleweapons" : "Battle Weapons",
    "bauxite" : "Bauxite",
    "beer" : "Beer",
    "benitoite" : "Benitoite",
    "bertrandite" : "Bertrandite",
    "beryllium" : "Beryllium",
    "bioreducinglichen" : "Bioreducing Lichen",
    "biowaste" : "Biowaste",
    "bismuth" : "Bismuth",
    "bootlegliquor" : "Bootleg Liquor",
    "bromellite" : "Bromellite",
    "buildingfabricators" : "Building Fabricators",
    "ceramiccomposites" : "Ceramic Composites",
    "chemicalwaste" : "Chemical Waste",
    "clothing" : "Clothing",
    "cmmcomposite" : "CMM Composite",
    "cobalt" : "Cobalt",
    "coffee" : "Coffee",
    "coltan" : "Coltan",
    "combatstabilisers" : "Combat Stabilisers",
    "comercialsamples" : "Commercial Samples",
    "computercomponents" : "Computer Components",
    "conductivefabrics" : "Conductive Fabrics",
    "consumertechnology" : "Consumer Technology",
    "coolinghoses" : "Micro-weave Cooling Hoses",
    "copper" : "Copper",
    "cropharvesters" : "Crop Harvesters",
    "cryolite" : "Cryolite",
    "damagedescapepod" : "Damaged Escape Pod",
    "datacore" : "Data Core",
    "diagnosticsensor" : "Hardware Diagnostic Sensor",
    "diplomaticbag" : "Diplomatic Bag",
    "domesticappliances" : "Domestic Appliances",
    "drones" : "Limpets",
    "duradrives" : "Duradrives",
    "earthrelics" : "Earth Relics",
    "emergencypowercells" : "Emergency Power Cells",
    "encripteddatastorage" : "Encrypted Data Storage",
    "encryptedcorrespondence" : "Encrypted Correspondence",
    "evacuationshelter" : "Evacuation Shelter",
    "exhaustmanifold" : "Exhaust Manifold",
    "explosives" : "Explosives",
    "fish" : "Fish",
    "foodcartridges" : "Food Cartridges",
    "fossilremnants" : "Fossil Remnants",
    "fruitandvegetables" : "Fruit and Vegetables",
    "gallite" : "Gallite",
    "gallium" : "Gallium",
    "genebank" : "Gene Bank",
    "geologicalequipment" : "Geological Equipment",
    "geologicalsamples" : "Geological Samples",
    "gold" : "Gold",
    "goslarite" : "Goslarite",
    "grain" : "Grain",
    "grandidierite" : "Grandidierite",
    "hafnium178" : "Hafnium 178",
    "hazardousenvironmentsuits" : "H.E. Suits",
    "heatsinkinterlink" : "Heatsink Interlink",
    "heliostaticfurnaces" : "Microbial Furnaces",
    "hnshockmount" : "HN Shock Mount",
    "hostage" : "Hostages",
    "hydrogenfuel" : "Hydrogen Fuel",
    "hydrogenperoxide" : "Hydrogen Peroxide",
    "imperialslaves" : "Imperial Slaves",
    "indite" : "Indite",
    "indium" : "Indium",
    "insulatingmembrane" : "Insulating Membrane",
    "iondistributor" : "Ion Distributor",
    "jadeite" : "Jadeite",
    "landmines" : "Landmines",
    "lanthanum" : "Lanthanum",
    "largeexplorationdatacash" : "Large Survey Data Cache",
    "leather" : "Leather",
    "lepidolite" : "Lepidolite",
    "liquidoxygen" : "Liquid oxygen",
    "liquor" : "Liquor",
    "lithium" : "Lithium",
    "lithiumhydroxide" : "Lithium Hydroxide",
    "lowtemperaturediamond" : "Low Temperature Diamonds",
    "magneticemittercoil" : "Magnetic Emitter Coil",
    "marinesupplies" : "Marine Equipment",
    "medicaldiagnosticequipment" : "Medical Diagnostic Equipment",
    "metaalloys" : "Meta-Alloys",
    "methaneclathrate" : "Methane Clathrate",
    "methanolmonohydratecrystals" : "Methanol Monohydrate Crystals",
    "microcontrollers" : "Micro Controllers",
    "militarygradefabrics" : "Military Grade Fabrics",
    "militaryintelligence" : "Military Intelligence",
    "mineralextractors" : "Mineral Extractors",
    "mineraloil" : "Mineral Oil",
    "modularterminals" : "Modular Terminals",
    "moissanite" : "Moissanite",
    "monazite" : "Monazite",
    "musgravite" : "Musgravite",
    "mutomimager" : "Muon Imager",
    "mysteriousidol" : "Mysterious Idol",
    "nanobreakers" : "Nanobreakers",
    "nanomedicines" : "Nanomedicines",
    "naturalfabrics" : "Natural Fabrics",
    "neofabricinsulation" : "Neofabric Insulation",
    "nerveagents" : "Nerve Agents",
    "nonlethalweapons" : "Non-Lethal Weapons",
    "occupiedcryopod" : "Occupied Escape Pod",
    "opal" : "Void Opal",
    "osmium" : "Osmium",
    "painite" : "Painite",
    "palladium" : "Palladium",
    "performanceenhancers" : "Performance Enhancers",
    "personaleffects" : "Personal Effects",
    "personalweapons" : "Personal Weapons",
    "pesticides" : "Pesticides",
    "platinum" : "Platinum",
    "politicalprisoner" : "Political Prisoners",
    "polymers" : "Polymers",
    "powerconverter" : "Power Converter",
    "powergenerators" : "Power Generators",
    "powergridassembly" : "Energy Grid Assembly",
    "powertransferconduits" : "Power Transfer Bus",
    "praseodymium" : "Praseodymium",
    "preciousgems" : "Precious Gems",
    "progenitorcells" : "Progenitor Cells",
    "prohibitedresearchmaterials" : "Prohibited Research Materials",
    "pyrophyllite" : "Pyrophyllite",
    "radiationbaffle" : "Radiation Baffle",
    "reactivearmour" : "Reactive Armour",
    "reinforcedmountingplate" : "Reinforced Mounting Plate",
    "resonatingseparators" : "Resonating Separators",
    "rhodplumsite" : "Rhodplumsite",
    "robotics" : "Robotics",
    "rockforthfertiliser" : "Rockforth Fertiliser",
    "rutile" : "Rutile",
    "samarium" : "Samarium",
    "sap8corecontainer" : "SAP 8 Core Container",
    "scientificresearch" : "Scientific Research",
    "scientificsamples" : "Scientific Samples",
    "scrap" : "Scrap",
    "semiconductors" : "Semiconductors",
    "serendibite" : "Serendibite",
    "silver" : "Silver",
    "skimercomponents" : "Skimmer Components",
    "slaves" : "Slaves",
    "smallexplorationdatacash" : "Small Survey Data Cache",
    "spacepioneerrelics" : "Space Pioneer Relics",
    "structuralregulators" : "Structural Regulators",
    "superconductors" : "Superconductors",
    "surfacestabilisers" : "Surface Stabilisers",
    "survivalequipment" : "Survival Equipment",
    "syntheticfabrics" : "Synthetic Fabrics",
    "syntheticmeat" : "Synthetic Meat",
    "syntheticreagents" : "Synthetic Reagents",
    "taaffeite" : "Taaffeite",
    "tacticaldata" : "Tactical Data",
    "tantalum" : "Tantalum",
    "tea" : "Tea",
    "telemetrysuite" : "Telemetry Suite",
    "terrainenrichmentsystems" : "Land Enrichment Systems",
    "thallium" : "Thallium",
    "thargoidheart" : "Thargoid Heart",
    "thargoidscouttissuesample" : "Thargoid Scout Tissue Sample",
    "thargoidtissuesampletype1" : "Thargoid Cyclops Tissue Sample",
    "thargoidtissuesampletype2" : "Thargoid Basilisk Tissue Sample",
    "thargoidtissuesampletype3" : "Thargoid Medusa Tissue Sample",
    "thargoidtissuesampletype4" : "Thargoid Hydra Tissue Sample",
    "thermalcoolingunits" : "Thermal Cooling Units",
    "thorium" : "Thorium",
    "timecapsule" : "Time Capsule",
    "titanium" : "Titanium",
    "tobacco" : "Tobacco",
    "toxicwaste" : "Toxic Waste",
    "trinketsoffortune" : "Trinkets of Hidden Fortune",
    "unknownartifact" : "Thargoid Sensor",
    "unknownartifact2" : "Thargoid Probe",
    "unknownartifact3" : "Thargoid Link",
    "unknownbiologicalmatter" : "Thargoid Biological Matter",
    "unknownresin" : "Thargoid Resin",
    "unknowntechnologysamples" : "Thargoid Technology Samples",
    "unstabledatacore" : "Unstable Data Core",
    "uraninite" : "Uraninite",
    "uranium" : "Uranium",
    "usscargoancientartefact" : "Ancient Artefact",
    "usscargoblackbox" : "Black Box",
    "usscargoexperimentalchemicals" : "Experimental Chemicals",
    "usscargomilitaryplans" : "Military Plans",
    "usscargoprototypetech" : "Prototype Tech",
    "usscargorareartwork" : "Rare Artwork",
    "usscargorebeltransmissions" : "Rebel Transmissions",
    "usscargotechnicalblueprints" : "Technical Blueprints",
    "usscargotradedata" : "Trade Data",
    "water" : "Water",
    "waterpurifiers" : "Water Purifiers",
    "wine" : "Wine",
    "wreckagecomponents" : "Wreckage Components"
 }