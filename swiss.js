var participantsById = {};

document.addEventListener('DOMContentLoaded', function() {
    showTab('participants'); // Show the first tab by default
    fetchParticipants(); // Fetch participants on load
    fetchMatches(); // Fetch matches on load

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


});

function showTab(tabName) {
    // Function to switch between tabs
    var i, tabcontent;
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    document.getElementById(tabName).style.display = "block";
}

function fetchParticipants() {
    fetch('http://localhost:5000/get-participants-sort-score')
        .then(response => response.json())
        .then(participants => {
        	var table = document.getElementById("participantsTable").getElementsByTagName('tbody')[0];
            table.innerHTML = ""; // Clear existing rows
            participants.forEach(participant => {
                participantsById[participant.id] = participant.name; // for matches table

                var row = table.insertRow();
                row.insertCell(0).innerHTML = participant.id;
                row.insertCell(1).innerHTML = participant.name;
                row.insertCell(2).innerHTML = parseFloat(participant.score).toFixed(3);
            });
        });

    fetch('http://localhost:5000/get-participants-sort-name')
        .then(response => response.json())
        .then(participants => {
            var participant1Dropdown = document.getElementById("participant1Dropdown");
            var participant2Dropdown = document.getElementById("participant2Dropdown");
            participant1Dropdown.innerHTML = ''; // Clear existing options
            participant2Dropdown.innerHTML = ''; // Clear existing options

            participants.forEach(participant => {
                var option1 = document.createElement("option");
                option1.value = participant.id;
                option1.text = participant.name;
                participant1Dropdown.add(option1);

                var option2 = document.createElement("option");
                option2.value = participant.id;
                option2.text = participant.name;
                participant2Dropdown.add(option2);
            });
        });
}


function addParticipant() {
    var name = document.getElementById('participantName').value;
    fetch('http://localhost:5000/add-participant', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: name, score: 0 })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data.message);
        fetchParticipants(); // Reload participants
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function fetchMatches() {
    fetch('http://localhost:5000/get-matches')
        .then(response => response.json())
        .then(matches => {
            var table = document.getElementById("matchesTable").getElementsByTagName('tbody')[0];
            table.innerHTML = ""; // Clear existing rows
            matches.forEach(match => {
                var row = table.insertRow();
                row.insertCell(0).innerHTML = participantsById[parseInt(match.participant1_id)] || 'Unknown';
                row.insertCell(1).innerHTML = participantsById[parseInt(match.participant2_id)] || 'Unknown';
                row.insertCell(2).innerHTML = match.participant1_wins;
                row.insertCell(3).innerHTML = match.participant2_wins;
            });
        });
}
function addMatch() {
    var participant1Id = document.getElementById('participant1Dropdown').value;
    var participant1Wins = document.getElementById('participant1Wins').value;
    var participant2Id = document.getElementById('participant2Dropdown').value;
    var participant2Wins = document.getElementById('participant2Wins').value;

    fetch('http://localhost:5000/add-match', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            participant1_id: participant1Id,
            participant1_wins: participant1Wins,
            participant2_id: participant2Id,
            participant2_wins: participant2Wins
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Show success message
        fetchMatches(); // Reload matches
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function recalculateScores() {
    fetch('http://localhost:5000/recalculate-scores', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Show success message
        fetchParticipants(); // Reload participants to update scores
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


