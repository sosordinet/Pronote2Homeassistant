import pronotepy
import os
from datetime import date
from datetime import timedelta 
import json

#Variables a remplacer (ou laisser comme ça pour tester la démo
eleve="demo" #nom de votre enfant - ne sert que pour le nom du fichier json
prefix_url = "demo" # sert au prefix de l'url https://PREFIX.index-education.net/pronote/
username="demonstration" #utlisateur pronote  - a remplacer par le nom d'utilisateur pronote de l'élève
password="pronotevs" # mot de passe pronote - a remplacer par le mot de passe du compte de l'élève

index_note=0 
limit_note=11 #nombre max de note à afficher + 1 
longmax_devoir = 125 #nombre de caractère max dans la description des devoirs

#Connection à Pronote 
client = pronotepy.Client('https://'+prefix_url+'.index-education.net/pronote/eleve.html?login=true', username, password)

#Si on est bien connecté
if client.logged_in:
    
    #Récupération  emploi du temps du jour
    lessons_today = client.lessons(date.today())
    lessons_today = sorted(lessons_today, key=lambda lesson: lesson.start)

    #Récupération  emploi du lendemain
    lessons_tomorrow = client.lessons(date.today()+ timedelta(days = 1))
    lessons_tomorrow = sorted(lessons_tomorrow, key=lambda lesson: lesson.start)
    delta = 1

    #Récupération  emploi du prochain jour d'école (ça sert le weekend et les vacances)
    lessons_nextday = client.lessons(date.today()+ timedelta(days = delta))
    while not lessons_nextday:
        lessons_nextday = client.lessons(date.today()+ timedelta(days = delta))
        delta = delta + 1 
    lessons_nextday = sorted(lessons_nextday, key=lambda lesson: lesson.start)

    #Transformation Json des emplois du temps (J,J+1 et next)
    jsondata = {}
    jsondata['edt_aujourdhui'] = []
    for lesson in lessons_today:
        jsondata['edt_aujourdhui'].append({
            'id': lesson.id,
            'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
            'date': lesson.start.strftime("%d/%m/%Y"),
            'heure': lesson.start.strftime("%H:%M"),
            'heure_fin': lesson.end.strftime("%H:%M"),
            'cours': lesson.subject.name,
            'salle': lesson.classroom,
            'annulation': lesson.canceled,
            'status': lesson.status,
            'background_color': lesson.background_color,
    })
    jsondata['edt_demain'] = []
    for lesson in lessons_tomorrow:
        jsondata['edt_demain'].append({
            'id': lesson.id,            
            'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
            'date': lesson.start.strftime("%d/%m/%Y"),
            'heure': lesson.start.strftime("%H:%M"),
            'heure_fin': lesson.end.strftime("%H:%M"),            
            'cours': lesson.subject.name,
            'salle': lesson.classroom,
            'annulation': lesson.canceled,
            'status': lesson.status,
            'background_color': lesson.background_color,
    })

    jsondata['edt_prochainjour'] = []
    for lesson in lessons_nextday:
        jsondata['edt_prochainjour'].append({
            'id': lesson.id,            
            'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
            'date': lesson.start.strftime("%d/%m/%Y"),
            'heure': lesson.start.strftime("%H:%M"),
            'heure_fin': lesson.end.strftime("%H:%M"),            
            'cours': lesson.subject.name,
            'salle': lesson.classroom,
            'annulation': lesson.canceled,
            'status': lesson.status,
            'background_color': lesson.background_color,
    })

    #Récupération des notes 
    grades = client.current_period.grades
    grades = sorted(grades, key=lambda grade: grade.date, reverse=True)

    #Transformation des notes en Json
    jsondata['note'] = []
    for grade in grades:
        index_note += 1
        if index_note == limit_note:
            break
        jsondata['note'].append({
            'date': grade.date.strftime("%d/%m/%Y"),
            'date_courte': grade.date.strftime("%d/%m"),            
            'cours': grade.subject.name,
            'note': grade.grade,            
            'sur': grade.out_of,
            'note_sur': grade.grade+'\u00A0/\u00A0'+grade.out_of,
            'coeff': grade.coefficient,
            'moyenne_classe': grade.average,           
            'max': grade.max,
            'min': grade.min,

    })

    #Récupération des devoirs
    homework_today = client.homework(date.today())
    homework_today = sorted(homework_today, key=lambda lesson: lesson.date)
    jsondata['devoir'] = []

    #Transformation des devoirs  en Json   
    for homework in homework_today:
        jsondata['devoir'].append({
            'date': homework.date.strftime("%d/%m"),
            'title': homework.subject.name,
            'description': (homework.description)[0:longmax_devoir],
            'description_longue': (homework.description),
            'done' : homework.done,            
    })
        
    #Récupération  des absences pour le trimestre en cours
    absences_current = client.current_period.absences()
    
    #Transformation des absences en Json
    jsondata['absences'] = []
    for absence in absences_current:
        jsondata['absences'].append({

            'id': absence.id,  
            'from_date_short': absence.from_date.strftime("%Y/%m/%d"),
            'from_date': absence.from_date.strftime("%d/%m/%Y %H:%M"),
            'to_date': absence.to_date.strftime("%d/%m/%Y %H:%M"), 
            'justified': absence.justified, 
            'hours': absence.hours, 
            'days': absence.days, 
            'reasons': absence.reasons,

    })
        
    #Récupération  des absences pour l'année
    all_absences = [period.absences for period in client.periods]
    
    #Transformation des absences pour l'année en Json
    jsondata['absences_all'] = []
    for period in all_absences:
        for absence in period():
   
          jsondata['absences_all'].append({
            
            'id':(f'{absence.id}'),
            'from_date':(f'{absence.from_date.strftime("%d/%m/%y %H:%M")}'),
            'from_date_short':(f'{absence.from_date.strftime("%Y/%m/%d")}'),
            'to_date':(f'{absence.to_date.strftime("%d/%m/%y %H:%M")}'),
            'justified':(f'{absence.justified}'),
            'hours':(f'{absence.hours}'),
            'days':(f'{absence.days}'),
            'reasons':(f'{absence.reasons}'),
            
    })
    #Récupération  des acquisitions + évaluations pour l'année
    all_acquisitions = [period.evaluations for period in client.periods]
    
    #Transformation des acquisitions en Json
    jsondata['acquisitions_all'] = []
    for period in all_acquisitions:
        for evaluation in period:
            for acquisition in evaluation.acquisitions:
   
                jsondata['acquisitions_all'].append({
            

                     'id':acquisition.id,
                     'pillar':acquisition.pillar,
                     'domain':acquisition.domain,
                     'order':acquisition.order,
                     'level':acquisition.level,
                     'abbreviation':acquisition.abbreviation,
                     'coefficient':acquisition.coefficient,
                     'name': evaluation.name,
                     'domain': evaluation.domain,
                     'teacher': evaluation.teacher,
                     'coefficient': evaluation.coefficient,
                     'description': evaluation.description,
                     'subject': evaluation.subject.name,
                     'paliers': evaluation.paliers,
                     'date': evaluation.date.strftime("%A %d %b %Y"),

    })
    
    information = client.information_and_surveys(only_unread=False)
    jsondata['info'] = []
    for info in information:
        for content in info.content:
            jsondata['info'].append({
                
                'id': info.id,
                'title': info.title,
                'auteur': info.author,
                'lu': info.read,
                'creation_date': info.creation_date.strftime("%Y/%m/%d"),
                'start_date': info.start_date.strftime("%Y/%m/%d"),
                'end_date': info.end_date.strftime("%Y/%m/%d"),
                'category': info.category,
                'anonymous_response': info.anonymous_response,
                'sondage': info.survey,
                '_raw_content': info._raw_content,
     
                })

    #Stockage dans un fichier json : edt + notes + devoirs 
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(location, "../www/pronote_"+eleve+".json"), "a") as outfile:
        outfile.truncate(0)
        json.dump(jsondata, outfile, indent=4)


    
 
