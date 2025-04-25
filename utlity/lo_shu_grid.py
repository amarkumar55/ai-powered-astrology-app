data = {
   "1": { 
      "title": "Leadership and Communication",
      "1" : "Indicative of introversion and difficulty in expressing feelings openly.",
      "2" : "Represents effective communication skills.",
      "3" : "Suggests a talkative nature, often seen as entertaining.",
      "4" : "Denotes a preference for written over verbal expression.",
      "remedis": "Donating wheat grains, rice, jaggery, and red clothes on Sundays; avoiding red and white clothing."
   },

   "2": {
      "title": "Sensitivity and Intuition",
      "1" : "Reflects sensitivity, emotional depth, and good intuition.",
      "2" : "Indicates intelligence and excellent judgment.",
      "3" : "Shows heightened intuition and quick decision-making but may lead to moodiness.",
      "4" : "Can result in quick temper and reactive behavior.",
      "remedis": "Donating white items like clothes, flowers, milk, and sugar on Mondays; avoiding white clothing."
   },

   "3": {
      "title": "Creativity and Imagination",
      "1" : "Denotes excellent memory and positive behavior.",
      "2" : "Represents strong creative abilities, suitable for writing.",
      "3" : "May lead to over-imagination and social withdrawal.",
      "4" : "Suggests a fearful and impractical approach to life",
      "remedis": "Donating yellow items like bananas, mangoes, flowers, and clothes on Thursdays; avoiding yellow clothing."
   },

   "4": {
      "title": "Practicality and Discipline",
      "1" : "Signifies a practical and orderly lifestyle.",
      "2" : "Indicates creativity and disciplined behavior.",
      "3" : "Represents hard work but potential difficulty in understanding others' perspectives.",
      "4" : "Points to a life requiring significant physical labor.",
      "remedis": "Donating black-blue clothes, wheat, and oil; avoiding black or blue clothing."
   },

   "5": {
      "title": "Adaptability and Courage",
      "1" : "Reflects an affectionate and inspiring personality.",
      "2" : "Denotes hard work, self-confidence, and emotional sensitivity.",
      "3" : "Suggests courage but a tendency for impulsive speech and risk-taking.",
      "4" : "Indicates overexcitement and a propensity for accidents.",
      "remedis": "Feeding cows with fodder and green leafy vegetables on Wednesdays; avoiding green clothing."
   },

   "6": {
      "title": "Harmony and Responsibility",
      "1" : "Represents a good adviser, partner, and family attachment.",
      "2" : "Shows a love for beauty and creativity.",
      "3" : "Can lead to tension, stress, and quick temper.",
      "4" : "Indicates excellence in creative activities but emotional vulnerability.",
      "remedis": "Donating sugar, milk, white flowers, white clothes, and ghee on Fridays; avoiding white clothing."
   },

   "7": {
      "title": "Learning and Spirituality",
      "1" : "Suggests learning from experiences and a spiritual inclination.",
      "2" : "Indicates gaining knowledge through setbacks.",
      "3" : "May lead to a life of sadness and disappointments​.",
      "4" : "Points to potential losses in love, health, and finance.",
      "remedis": "Donating grains, woolen clothes, and kajal on Tuesdays; avoiding green clothing."
   },

   "8": {
      "title": "Ambition and Material Success",
      "1" : "Indicates an uncomfortable life with mental challenges.",
      "2" : "Represents stubbornness and learning from mistakes.",
      "3" : "Shows a focus on materialistic pleasures with growth after 40.",
      "4" : "Suggests rapid progress in life.",
      "remedis": "Donating mustard oil, black clothes, and black blankets on Saturdays; avoiding black clothing."
   },

   "9": {
      "title": "Intelligence and Compassion",
      "1" : "Denotes intelligence, ambition, and self-improvement.",
      "2" : "Indicates wisdom and a sense of superiority.",
      "3" : "Reflects a helping nature but quick irritation.",
      "4" : "Represents high intelligence but difficulty in lying.",
      "remedis": "Donating red items like clothes, fruits, and flowers on Tuesdays; avoiding red clothing."
   },

   "1_5_9": {
      "1_5_9" : "Represents strong willpower, resilience, and the ability to overcome obstacles. Individuals with this arrow are often unwavering in pursuing their goals."
   },

   "4_5_9":{
      "4_5_9" : "Denotes a balanced and strong will, with a practical approach to challenges. Such individuals are decisive and persistent",       
   },

   "7_5_3":{
      "7_5_3": "Indicates high energy levels and a proactive nature. Individuals with this arrow are often dynamic and engage in various activities enthusiastically."
   },

   "2_5_8":{
      "2_5_8": "Reflects a nurturing and empathetic personality. These individuals are compassionate, understanding, and often involved in helping others."
   },

   "1_4_7": {
      "1_4_7": "Suggests a down-to-earth and pragmatic approach to life. Individuals with this arrow are methodical and efficient in their endeavors."
   },

   "3_5_7" : {
      "3_5_7": "Denotes emotional stability and maturity. Such individuals can manage their emotions effectively and maintain harmonious relationships."
   },

   "3_6_9": { 
      "3_6_9": "Represents analytical thinking, intelligence, and a keen mind. Individuals with this arrow excel in intellectual pursuits and problem-solving."
   },

}



# utility function to get meaning of each number present in date of birth 
def get_number_detail(num):
   return data[num]


 
# displaying Arrows of Strength 
def get_combination_available(key):
   return data[key];