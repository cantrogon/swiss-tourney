const participantsById = {};
let matchEdit = []; // hacky
let greatestMatchId = 0 // also hacky

document.addEventListener('DOMContentLoaded', async function() {
	showTab('participants');

	await initialiseParticipantIDs()
	setDropdownById('participant1Dropdown')
	setDropdownById('participant2Dropdown')

	matchesTable = initialiseMatchesTable()
	participantsTable = initialiseParticipantsTable()
	pairingsTable = initialisePairingsTable()

	reloadParticipants();
	reloadMatches();
	reloadPairings();

	document.getElementById('addParticipantForm').addEventListener('submit', function(e) {
		e.preventDefault();
		addParticipant();
	});

	document.getElementById('addMatchForm').addEventListener('submit', function(e) {
		e.preventDefault();
		addMatch();
	});

	document.getElementById('recalculateScoresButton').addEventListener('click', function() {
		recalculateScores();
	});

	document.getElementById('getPairingsButton').addEventListener('click', function() {
		reloadPairings();
	});

	document.getElementById('addPairingsButton').addEventListener('click', function() {
		addPairingsToMatches();
	});

});

function getPNameById(id) {
	return participantsById[parseInt(id)] || 'unknown';
}

function getPIdByName(id) {
	return Object.keys(participantsById).find(key => participantsById[key] === id);
}

function showTab(tabName) {
	// Function to switch between tabs
	let i, tabcontent;
	tabcontent = document.getElementsByClassName("tab-content");
	for (i = 0; i < tabcontent.length; i++) {
		tabcontent[i].style.display = "none";
	}
	document.getElementById(tabName).style.display = "block";
}

function initialiseParticipantIDs() {
	return fetch('http://localhost:5000/get-participants')
		.then(response => response.json())
		.then(participants => participants.map(p => participantsById[p.id] = p.name))
}

function setDropdownById(elmId) {
	let dropdownElm = document.getElementById(elmId);
	setDropdown(dropdownElm)
}

function createDropdown(startingVal=null) {
	const elm = document.createElement("select")
	setDropdown(elm, startingVal)
	return elm
}

function setDropdown(dropdownElm, startingVal=null) {
	const pNameId = Object.entries(participantsById).sort(([,a],[,b]) => a.localeCompare(b))
	pNameId.forEach(p => {
		const option = document.createElement("option")
		option.value = p[0]
		option.text = p[1]
		option.setAttribute("data-name", p[1])
		if (option.value === startingVal)
			option.setAttribute("selected", true)
		dropdownElm.add(option)
	});
}


function initialiseMatchesTable() {

	const container = document.querySelector("#matchesTable");

	function getDropdownHtml(startingName) {
		const startingVal = getPIdByName(startingName)
		const html = createDropdown(startingVal).outerHTML
		return html
	}

	const formatterDropdown = (cell, row) => {
		return row.cells[row.cells.length - 1].data ? gridjs.html(getDropdownHtml(cell)) : cell
	}

	const formatterNumber = (cell, row) => 
		row.cells[row.cells.length - 1].data ? gridjs.html(`<input type="number" value="${cell}"/>`) : cell

	const formatterEdit = (_, row) => 
		gridjs.html(`<button onclick="toggleEditSave(${row.rowIndex})">${row.cells[row.cells.length - 1].data ? 'Save' : 'Edit'}</button>`)

	function updateData(rowIndex, rowData) {
		const rowElm = document.querySelector(`#matchesTable tbody tr:nth-of-type(${rowIndex+1})`);
		
		const p1Id = rowElm.querySelector(`td[data-column-id=participant1] select`).value;
		const p2Id = rowElm.querySelector(`td[data-column-id=participant2] select`).value;
		const p1Wins = rowElm.querySelector(`td[data-column-id=p1Wins] input`).value;
		const p2Wins = rowElm.querySelector(`td[data-column-id=p2Wins] input`).value;
		const matchId = rowData[1]
		const roundId = rowData[2]
		
		updateMatch(p1Id, p2Id, p1Wins, p2Wins, matchId, roundId)
	}

	const buttonsFunc = (cell, row) => {
		// console.log(row, cell)
		// console.log(grid)
		// console.log(grid.config.columns)
		// console.log(row.cells)
		// cols[cols.length - 1].data = !cols[cols.length - 1].data; // Toggle edit mode
		// grid.updateConfig({data: grid.config.columns}).forceRender();

		const isEditing = matchEdit[row.cells[0].data]

		if (isEditing) {
			return gridjs.h('button', {
				onClick: () => {
					const cols = row.cells
					const rowIndex = cols[0].data
					const rowData = row.cells.map(x => x.data)
					updateData(rowIndex, rowData)
					matchEdit[rowIndex] = false
					grid.forceRender()
				}
			}, '✔');
		} else {
			return gridjs.h('button', {
				onClick: () => {
					const rowIndex = row.cells[0].data
					matchEdit[rowIndex] = true
					grid.forceRender()
				}
			}, '✎');
		}

	}

	const grid = new gridjs.Grid({
		columns: [
			{name: 'rowIndex', hidden: true},
			{name: 'ID', hidden: true},
			{name: 'Round', formatter: formatterNumber, hidden: true},
			{name: 'Participant 1', id: 'participant1', formatter: formatterDropdown},
			{name: 'Participant 2', id: 'participant2', formatter: formatterDropdown},
			{name: 'P1 Wins', id: 'p1Wins', formatter: formatterNumber, width: "120px"},
			{name: 'P2 Wins', id: 'p2Wins', formatter: formatterNumber, width: "120px"},
			// {name: 'Edit', formatter: buttonsFunc, data: false}
			{name: 'Edit', formatter: buttonsFunc, width: "70px", sort: false},
		],
		data: () => {
			return fetch('http://localhost:5000/get-matches')
				.then(res => res.json())
				.then(data => {
					if (matchEdit.length === 0) {
						matchEdit = Array(data.length).fill(false)
					}
					if (data.length > 0) {
						greatestMatchId = Math.max(...data.map(o => o.match_id))
					}

					return data.map((match, i) => [
						i,
						match.match_id,
						match.round_id,
						getPNameById(match.participant1_id),
						getPNameById(match.participant2_id),
						match.participant1_wins,
						match.participant2_wins,
						matchEdit[i],
					])
				})
		},
		sort: true
	}).render(container);

	return grid
}

function addPairingsToMatches() {
	return fetch('http://localhost:5000/get-pairings')
		.then(response => response.json())
		.then(async pairings => {
			// console.log(pairings)
			// pairings = [[p1Id, p2Id], ...]
			const data = []
			for (pair of pairings) {
				greatestMatchId++
				data.push({
					participant1_id: pair[0],
					participant1_wins: 0,
					participant2_id: pair[1],
					participant2_wins: 0,
					match_id: greatestMatchId,
					round_id: -1,
				})
			}
			postData('http://localhost:5000/add-matches', data, reloadMatches)

			// let callback = pairingsCallback(pairings.length, reloadMatches)
			// for (pair of pairings) {
			// 	greatestMatchId++
			// 	await postData(
			// 		'http://localhost:5000/add-match', 
			// 		{
			// 			participant1_id: pair[0],
			// 			participant1_wins: 0,
			// 			participant2_id: pair[1],
			// 			participant2_wins: 0,
			// 			match_id: greatestMatchId,
			// 			round_id: -1,
			// 		},
			// 		callback
			// 	)
			// }
		});
}

function pairingsCallback(n, callback) {
	let i = 0
	return function() {
		i++
		// console.log(i);
		if (i >= n) callback()
	}
}

function initialiseParticipantsTable() {

	let container = document.querySelector("#participantsTable");
	const grid = new gridjs.Grid({
		sort: true,
		columns: ['Rank', 'Score', 'Name', 'ID'],
		server: {
			url: 'http://localhost:5000/get-participants-sort-score',
			then: participants => {
				getRanking(participants)
				return participants.map(participant => [
					participant.rank,
					parseFloat(participant.score).toFixed(3),
					participant.name, 
					parseInt(participant.id)
				])
			}
		}
	}).render(container);
	return grid

}

function getRanking(participants) {
	
	const processedScores = participants.map(participant => parseFloat(participant.score).toFixed(3));

	let currentlyTying = false;
	let currentTieRank = 0;

	let ranks = [];
	for (let i = 0; i < participants.length; i++){
		const participant = participants[i];
		const score = processedScores[i];

		let rank;
		if (i !== participants.length - 1 && processedScores[i + 1] === score) { // If the tie chain will continue
			if (currentlyTying === false) { // If this is the start of a new tie chain, update the starting rank
				currentTieRank = i + 1;
			}
			currentlyTying = true;
			rank = "=" + currentTieRank; // Whether the chain is old or new, the rank has a = in it
			// rank = currentTieRank;
		} else {
			rank = currentlyTying ? "=" + currentTieRank : (i + 1).toString();
			// rank = currentlyTying ? currentTieRank : i + 1;
			currentlyTying = false;
		}
		participant.rank = rank
		ranks.push(rank)
	}
	return ranks
}


function initialisePairingsTable() {
	let container = document.querySelector("#pairingsTable");
	const grid = new gridjs.Grid({
		sort: true,
		columns: ['Participant 1', 'Participant 2'],
		server: {
			url: 'http://localhost:5000/get-pairings',
			then: pairs => {
				return pairs.map(pair => [
					getPNameById(pair[0]),
					getPNameById(pair[1]),
				])
			}
		}
	}).render(container);
	return grid
}

function reloadParticipants() {
	participantsTable.forceRender()
}

function reloadMatches() {
	matchesTable.forceRender()
}

function reloadPairings() {
	pairingsTable.forceRender()
}

function addParticipant() {
	let name = document.getElementById('participantName').value;
	postData(
		'http://localhost:5000/add-participant', 
		{ name: name, score: 0 },
		reloadParticipants
	)
}

function addMatch() {
	let participant1Id = document.getElementById('participant1Dropdown').value;
	let participant1Wins = document.getElementById('participant1Wins').value;
	let participant2Id = document.getElementById('participant2Dropdown').value;
	let participant2Wins = document.getElementById('participant2Wins').value;

	greatestMatchId++
	let matchId = greatestMatchId;
	addMatchSend(participant1Id, participant2Id, participant1Wins, participant2Wins, matchId)
}

function addMatchSend(p1Id, p2Id, p1Wins, p2Wins, matchId, roundId=-1) {
	postData(
		'http://localhost:5000/add-match', 
		{ 
			participant1_id: p1Id,
			participant1_wins: p1Wins,
			participant2_id: p2Id,
			participant2_wins: p2Wins,
			match_id: matchId,
			round_id: roundId,
		},
		reloadMatches
	)
}

function updateMatch(p1Id, p2Id, p1Wins, p2Wins, matchId, roundId=-1) {
	postData(
		'http://localhost:5000/edit-match', 
		{ 
			participant1_id: p1Id,
			participant1_wins: p1Wins,
			participant2_id: p2Id,
			participant2_wins: p2Wins,
			match_id: matchId,
			round_id: roundId,
		},
		reloadMatches
	)
}

function recalculateScores() {
	postData(
		'http://localhost:5000/recalculate-scores', 
		null,
		reloadParticipants
	)
}

function postData(url, data = null, callback = null) {
	let payload;
	if (data != null) {
		payload = {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(data)
		}
	} else {
		payload = {method: 'POST'}
	}

	return fetch(url, payload)
	.then(response => response.json())
	.then(data => {
		console.log(data.message);
		if (callback) callback()
	})
	.catch(error => {
		console.error('Error:', error);
	});
}

function fetchPairings() {
	fetch('http://localhost:5000/get-pairings')
		.then(response => response.json())
		.then(pairings => {
			let table = document.getElementById("matchesTable").getElementsByTagName('tbody')[0];
			table.innerHTML = ""; // Clear existing rows
			matches.forEach(match => {
				let row = table.insertRow();
				row.insertCell(0).innerHTML = participantsById[parseInt(match.participant1_id)] || 'Unknown';
				row.insertCell(1).innerHTML = participantsById[parseInt(match.participant2_id)] || 'Unknown';
				row.insertCell(2).innerHTML = match.participant1_wins;
				row.insertCell(3).innerHTML = match.participant2_wins;
			});
		});
}



function insertMatch(p1_id, p2_id, p1_wins, p2_wins) {
	let table = document.querySelector("#matchesTable tbody");
	table.innerHTML = "";
	matches.forEach(match => {
		let row = table.insertRow();
		row.insertCell(0).innerHTML = participantsById[parseInt(match.participant1_id)] || 'unknown';
		row.insertCell(1).innerHTML = participantsById[parseInt(match.participant2_id)] || 'unknown';
		row.insertCell(2).innerHTML = match.participant1_wins;
		row.insertCell(3).innerHTML = match.participant2_wins;
	});
}


