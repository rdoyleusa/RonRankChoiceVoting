# Implementation URL
# https://blog.opavote.com/2016/11/plain-english-explanation-of-scottish.html

# View Video Explanation
# https://www.fairvote.org/rcv#how_rcv_works (bottom video on "multi-winner")

# Building the CSV File:
# Candidate Names Should Be Assigned Randomly from Left to Right
# 
# In the event of a round #1 tie to elect or eliminate:
# Left-Most of Multiple-Tied Candidates will be Elected
# Right-Most of Multiple-Tied Candidated will be Eliminated

# Coded in Python 3.4.3 on Windows 10 PC

import csv
import math

# User Inputs:
seat_count = 6 #number of winners required
ballot_count = 30 #count of valid ballots prior to round 1

election_threshold = math.floor((ballot_count / (seat_count + 1)) + 1) # DO NOT CHANGE
election_round = 1

while (seat_count > 0):
    # Read in Candidate List and Raw Ballots from CSV File
    votes = []
    #csv_file_name = ("rc_votes_%d" % election_round)                                           
    with open('rc_votes_%d.csv' % election_round) as csvfile_in:      ## VOTE INPUT FILE FOR ROUND ##
        readCSV = csv.reader(csvfile_in, delimiter=',')
      
        candidates_list_read = False
        for row in readCSV:
            
            #print (row)
            if (candidates_list_read == True):
                temp = []
                for i in range(0, candidate_count + 1):
                    if (i == 0):
                        temp.append(float(row[i]))
                    else:
                        temp.append(int(row[i]))
                votes.append(temp)
            else:
                candidate_names = row.copy()
                candidate_names.pop(0)
                candidate_count = len(candidate_names)
                for i in range(candidate_count):
                    candidate_names[i] = candidate_names[i].strip()
                candidates_list_read = True

    print()
    print("Candidate Count:",candidate_count)
    print("Ballot Count:",ballot_count)
    print("Threshold:",election_threshold)
    print()

    # Aggregate Duplicate Ballot Results into Weighted Ballots
    vote_count = len (votes)
    x = 0
    y = 1
    while (y < vote_count):
        while (y < vote_count):
            temp_x = votes[x].copy()
            temp_y = votes[y].copy()
            temp_x.pop(0)
            temp_y.pop(0)
            if (temp_x == temp_y):
                votes[x][0] += votes[y][0]
                votes.pop(y)
                vote_count -= 1
            else:
                y += 1
                
        x += 1
        y = x + 1    

    # Initialize ballot count by candidate
    candidate_ballot_count = []
    candidate_ballot = []
    for x in range(candidate_count):
        candidate_ballot_count.append(0.0)

    # Tabulation and assignment of weighted ballots to candidates
    for ballot in votes:
        for j in range(0, candidate_count):
            if ((ballot[j + 1]) == 1):
                candidate_ballot_count[j] += ballot[0]    

    for x in range(candidate_count):
        print (candidate_names[x]," has ", candidate_ballot_count[x]," votes")

    # EITHER Elect a Candidate and Transfer Surplus Votes...
    if ((max(candidate_ballot_count) >= election_threshold) or (candidate_count <= seat_count)):
        x = 0
        while (candidate_ballot_count[x] != max(candidate_ballot_count)):
            x += 1

        print ()
        print (candidate_names[x],"is elected with",candidate_ballot_count[x],"votes.\n")
        candidate_names.pop(x)
        
        # transfer surplus votes for elected candidate to next choice
        total_votes_for_winner = max(candidate_ballot_count)
        if (total_votes_for_winner > election_threshold):
            surplus_votes_for_winner = total_votes_for_winner - election_threshold
        else:
            surplus_votes_for_winner = 0
        candidate_ballot_count.pop(x)
        
        for ballot in votes:
            if (ballot[x + 1] == 1):
                ballot[0] = ballot[0] * surplus_votes_for_winner / total_votes_for_winner
                for y in range (1, candidate_count + 1):
                    if (ballot[y] > 0):
                        ballot[y] -= 1

            ballot.pop(x + 1) # elected, so can no longer receive votes in later rounds
            
        seat_count -= 1

    # ... OR Eliminate a Candidate and Transfer Votes
    else:
        x = len(candidate_ballot_count) - 1
        while (candidate_ballot_count[x] != min(candidate_ballot_count)):
            x -= 1
            
        print ()
        print (candidate_names[x],"is eliminated with",candidate_ballot_count[x],"votes.\n")
        candidate_names.pop(x)
                
        # transfer all votes for eliminated candidate to next choice
        total_votes_for_loser = min(candidate_ballot_count)
        candidate_ballot_count.pop(x)
        
        for ballot in votes:
            if (ballot[x + 1] == 1):
                for y in range (1, candidate_count + 1):
                    if (ballot[y] > 0):
                        ballot[y] -= 1

            ballot.pop(x + 1) # eliminated, so can no longer receive votes in later rounds

    # Reorder updated ballot table left-to-right by current rank
    updated_candidate_names = []
    for z in range(len(candidate_ballot_count)):
        x = 0
        while (candidate_ballot_count[x] != max(candidate_ballot_count)):
            x += 1
        
        updated_candidate_names.append(candidate_names[x])
        for ballot in votes:
            ballot.append(ballot[x + 1])

        candidate_ballot_count[x] = -1

    for z in range(len(candidate_ballot_count)):
        for ballot in votes:
            ballot.pop(1)

    # Write updated ballot table to file
    election_round += 1
    
    with open('rc_votes_%d.csv' % election_round, mode='w') as csvfile_out: ### VOTE OUTPUT FILE FOR ROUND ###
        writeCSV = csv.writer(csvfile_out, delimiter=',', lineterminator='\n')

        updated_candidate_names.insert(0, "Weight")
        writeCSV.writerow(updated_candidate_names)
        for ballot in votes:
            if (ballot[0] > 0):         # Remove weightless ballots
                temp_y = ballot.copy()
                temp_y.pop(0)
                if 1 in temp_y:         # Remove exhausted ballots
                    writeCSV.writerow(ballot)            
