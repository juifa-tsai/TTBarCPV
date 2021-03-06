#!/usr/bin/env python
import os, re, sys, shutil
import math, ROOT
import numpy

#if sys.argv[1] == '':
#	print ""
#	print sys.argv[0]

from fuctions import*
from PIDs import PIDs  

printEvt=6

pids = PIDs('decayList.txt')
pids.loadDecayList()

#lheFile = open('example_TTtoDiMuon_UnWrtEvents.lhe');
#lheFile = open('unweighted_events.lhe');
lheFile = open('unweighted_events_v2.lhe');
LHEVersion=''
MGVersion=''
MG5ProcCard=''
MGProcCard=''
MGRunCard=''
slha=''
init=''
evtTable=[]
tags = { 'MGVersion':0, 
         'MG5ProcCard':0,
         'MGProcCard':0,
         'MGRunCard':0,
         'slha':0,
         'init':0, 
         'event':0, 
} # 0: Off, 1: On, 2: Done 

def switchTag(l, tags):
	if l.find('<MGVersion')   >= 0:  tags['MGVersion'] = 1
	if l.find('</MGVersion')  >= 0:  tags['MGVersion'] =-1
	if l.find('<MG5ProcCard') >= 0:  tags['MG5ProcCard'] = 1
	if l.find('</MG5ProcCard')>= 0:  tags['MG5ProcCard'] =-1
	if l.find('<MGProcCard') >= 0:   tags['MGProcCard'] = 1
	if l.find('</MGProcCard')>= 0:   tags['MGProcCard'] =-1
	if l.find('<MGRunCard')   >= 0:  tags['MGRunCard'] = 1
	if l.find('</MGRunCard')  >= 0:  tags['MGRunCard'] =-1
	if l.find('<slha')  >= 0:        tags['slha'] = 1
	if l.find('</slha') >= 0:        tags['slha'] =-1
	if l.find('<init')  >= 0:        tags['init'] = 1
	if l.find('</init') >= 0:        tags['init'] =-1
	if l.find('<event') >= 0:        tags['event'] = 1
	if l.find('</event')>= 0:        tags['event'] =-1

###### * Load and store info from lhe file
print 'Loading lhe...'
numEvt=-1
for line in lheFile:

	l = line.strip()
	if isEmpty(l):
		continue

	if l.find('<LesHouchesEvents') >= 0: 
		LHEVersion = l.split('="')[1].split('">')[0]	
		 
	switchTag(l, tags)
	if tags['MGVersion'] == 1 and l.find('<MGVersion') < 0:
		MGVersion = MGVersion + l + "\n"
	if tags['MG5ProcCard'] == 1 and l.find('<MG5ProcCard') < 0:
		MG5ProcCard = MG5ProcCard + l + "\n"
	if tags['MGProcCard'] == 1 and l.find('<MGProcCard') < 0:
		MGProcCard = MGProcCard + l + "\n"
	if tags['MGRunCard'] == 1 and l.find('<MGRunCard') < 0:
		MGRunCard = MGRunCard + l + "\n"
	if tags['slha'] == 1 and l.find('<slha') < 0:
		slha = slha + l + "\n"
	if tags['init'] == 1 and l.find('<init') < 0:
		init = init + l + "\n"
	if tags['event'] == 1 and l.find('<event') < 0:
		if isComment(l): 
			continue
		if len(l.split()) == 6:
			numEvt += 1	
			evtTable.append(l)
		else:
			evtTable[numEvt] = evtTable[numEvt] + "\n" + l 

###### * Load event table and print out
#print MGProcCard
GMProcess=[]
for line in MGProcCard.splitlines():
	if isComment(line): 
		continue
	if line.find('#Process') >= 0:
		GMProcess.append(line.split('#')[0].strip())

print 'Loading Events...'
i=0
while ( i < printEvt ):
		evtInfo_numParticle = ''	
		evtInfo_idProcess   = ''	
		evtInfo_evtWrt      = ''	
		evtInfo_scalePDF    = ''	
		evtInfo_aQED    	= ''	
		evtInfo_aQCD    	= ''	
		particleInfo_pid   	= []
		particleInfo_status = []
		particleInfo_moth1  = []
		particleInfo_moth2  = []
		particleInfo_Nmoth  = []
		particleInfo_dau1   = []
		particleInfo_dau2   = []
		particleInfo_dau3   = []								# Sometimes heppand
		particleInfo_Ndau   = []
		particleInfo_color1 = []
		particleInfo_color2 = []
		particleInfo_px     = []
		particleInfo_py     = []
		particleInfo_pz     = []
		particleInfo_energy = []
		particleInfo_mass   = []
		particleInfo_invLifeTimie = []                           # without secondary vertex, which depend on generating setup
		particleInfo_helicity     = []
		p=0
		for row in evtTable[i].splitlines():
			if len( row.split() ) == 6:                          # Fist line of event table, which contain event information
				evtInfo_numParticle = int(row.split()[0])
				evtInfo_idProcess   = int(row.split()[1])
				evtInfo_evtWrt      = float(row.split()[2])	
				evtInfo_scalePDF    = float(row.split()[3])	
				evtInfo_aQED    	= float(row.split()[4])	
				evtInfo_aQCD    	= float(row.split()[5])
				k=0
				while ( k < evtInfo_numParticle):
					particleInfo_Nmoth.append(0)
					particleInfo_Ndau .append(0)
					particleInfo_dau1 .append(-1)
					particleInfo_dau2 .append(-1)
					particleInfo_dau3 .append(-1)
					k+=1	
			elif len( row.split() ) == 13:                       # Particle information 
				particleInfo_pid   .append(int(row.split()[0]))
				particleInfo_status.append(int(row.split()[1]))
				particleInfo_moth1 .append(int(row.split()[2])-1)
				particleInfo_moth2 .append(int(row.split()[3])-1)
				particleInfo_color1.append(int(row.split()[4]))
				particleInfo_color2.append(int(row.split()[5]))
				particleInfo_px    .append(float(row.split()[6]))
				particleInfo_py    .append(float(row.split()[7]))
				particleInfo_pz    .append(float(row.split()[8]))
				particleInfo_energy.append(float(row.split()[9]))
				particleInfo_mass  .append(float(row.split()[10]))
				particleInfo_invLifeTimie.append(float(row.split()[11]))
				particleInfo_helicity    .append(float(row.split()[12]))
				## * Count daughters
				if particleInfo_moth1[p] == particleInfo_moth2[p] and particleInfo_moth1[p] != -1:
					particleInfo_Nmoth[p] = 1
					particleInfo_Ndau[particleInfo_moth1[p]] += 1
				elif particleInfo_moth1[p] != particleInfo_moth2[p] and particleInfo_moth1[p] != -1 and particleInfo_moth2[p] != -1:
					particleInfo_Nmoth[p] = 2
					particleInfo_Ndau[particleInfo_moth1[p]] += 1
					particleInfo_Ndau[particleInfo_moth2[p]] += 1
				p+=1	

		## * Store daughters
		p=0
		while ( p < evtInfo_numParticle ):

			if particleInfo_dau1[particleInfo_moth1[p]] == -1 and particleInfo_Ndau[particleInfo_moth1[p]] > 0:
				particleInfo_dau1[particleInfo_moth1[p]] = p
			elif particleInfo_dau1[particleInfo_moth1[p]] > -1 and particleInfo_dau2[particleInfo_moth1[p]] == -1:
				particleInfo_dau2[particleInfo_moth1[p]] = p
			elif particleInfo_dau1[particleInfo_moth1[p]] > -1 and particleInfo_dau2[particleInfo_moth1[p]] > -1 and particleInfo_dau3[particleInfo_moth1[p]] == -1:
				particleInfo_dau3[particleInfo_moth1[p]] = p

			if particleInfo_dau1[particleInfo_moth2[p]] == -1 and particleInfo_Ndau[particleInfo_moth2[p]] > 0:
				particleInfo_dau1[particleInfo_moth2[p]] = p
			elif particleInfo_dau1[particleInfo_moth2[p]] > -1 and particleInfo_dau2[particleInfo_moth2[p]] == -1 and particleInfo_dau1[particleInfo_moth2[p]] != p:
				particleInfo_dau2[particleInfo_moth2[p]] = p
			elif particleInfo_dau1[particleInfo_moth2[p]] > -1 and particleInfo_dau2[particleInfo_moth2[p]] > -1 and particleInfo_dau3[particleInfo_moth2[p]] == -1 and particleInfo_dau3[particleInfo_moth2[p]] != p:
				particleInfo_dau3[particleInfo_moth2[p]] = p
			p+=1
	
		## * Print out event information 
		print '\n.----------------------------------------------------------------------------------.' 
		print '| *** Event '+str(i)+' **** ----------------------------------------------------------------|'
		print '|----------------------------------------------------------------------------------|' 
		print '| Status = -1 : Incoming particle                                                  |' 
		print '|          +1 : Outgoing final state particle                                      |'
		print '|          -2 : Intermediate space-like propagator, x and Q2 shell be preserved    |' 
		print '|          +2 : Intermediate resonance, Mass should be preserved                   |' 				
		print '|          +3 : Intermediate resonance, for documentation only                     |' 				
		print '|          -9 : Incoming beam particles at time t = -oo                            |' 			

		for pro in GMProcess:
			print '| MG5 Process : %-67s|' % pro				
				
		print '| Number of particle : %2d                                                          |' % evtInfo_numParticle				
		print '|----------------------------------------------------------------------------------|' 
		print '| {0:20s}{1:6s} {2:7s} {3:7s} {4:8s} {5:8s} {6:6s} |'.format('Particle chain', ' | Status','|   Px  ', ' |    Py  ', '|    Pz   ', '|  Energy ', '|  Mass ')
		p=0
		while ( p < evtInfo_numParticle ):
			print '|----------------------------------------------------------------------------------|' 
			print '| {0:20s} | {1:+4d}   | {2:7.2f} | {3:7.2f} | {4:8.2f} | {5:8.2f} | {6:6.2f} |'.format(pids.showName(particleInfo_pid[p]), particleInfo_status[p], particleInfo_px[p], particleInfo_py[p], particleInfo_pz[p], particleInfo_energy[p], particleInfo_mass[p])
			dua1=particleInfo_dau1[p]
			dua2=particleInfo_dau2[p]
			dua3=particleInfo_dau3[p]
			if particleInfo_Ndau[p] == 3:
				print '| {0:20s} | {1:+4d}   | {2:7.2f} | {3:7.2f} | {4:8.2f} | {5:8.2f} | {6:6.2f} |'.format('|-> '+pids.showName(particleInfo_pid[dua1]), particleInfo_status[dua1], particleInfo_px[dua1], particleInfo_py[dua1], particleInfo_pz[dua1], particleInfo_energy[dua1], particleInfo_mass[dua1])
				print '| {0:20s} | {1:+4d}   | {2:7.2f} | {3:7.2f} | {4:8.2f} | {5:8.2f} | {6:6.2f} |'.format('|-> '+pids.showName(particleInfo_pid[dua2]), particleInfo_status[dua2], particleInfo_px[dua2], particleInfo_py[dua2], particleInfo_pz[dua2], particleInfo_energy[dua2], particleInfo_mass[dua2])
				print '| {0:20s} | {1:+4d}   | {2:7.2f} | {3:7.2f} | {4:8.2f} | {5:8.2f} | {6:6.2f} |'.format('`-> '+pids.showName(particleInfo_pid[dua3]), particleInfo_status[dua3], particleInfo_px[dua3], particleInfo_py[dua3], particleInfo_pz[dua3], particleInfo_energy[dua3], particleInfo_mass[dua3])
			elif particleInfo_Ndau[p] == 2:
				print '| {0:20s} | {1:+4d}   | {2:7.2f} | {3:7.2f} | {4:8.2f} | {5:8.2f} | {6:6.2f} |'.format('|-> '+pids.showName(particleInfo_pid[dua1]), particleInfo_status[dua1], particleInfo_px[dua1], particleInfo_py[dua1], particleInfo_pz[dua1], particleInfo_energy[dua1], particleInfo_mass[dua1])
				print '| {0:20s} | {1:+4d}   | {2:7.2f} | {3:7.2f} | {4:8.2f} | {5:8.2f} | {6:6.2f} |'.format('`-> '+pids.showName(particleInfo_pid[dua2]), particleInfo_status[dua2], particleInfo_px[dua2], particleInfo_py[dua2], particleInfo_pz[dua2], particleInfo_energy[dua2], particleInfo_mass[dua2])
			elif particleInfo_Ndau[p] == 1:
				print '| {0:20s} | {1:+4d}   | {2:7.2f} | {3:7.2f} | {4:8.2f} | {5:8.2f} | {6:6.2f} |'.format('`-> '+pids.showName(particleInfo_pid[dua1]), particleInfo_status[dua1], particleInfo_px[dua1], particleInfo_py[dua1], particleInfo_pz[dua1], particleInfo_energy[dua1], particleInfo_mass[dua1])
			p+=1

		i+=1	
		print '`----------------------------------------------------------------------------------\'' 


