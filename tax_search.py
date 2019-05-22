from Bio import Entrez


def main():
   file = open("blast_results.csv", "r")
   accessiecodelijst = accessiecodelijstmaker(file)
   print(accessiecodelijst)

   refseqzoeker(accessiecodelijst)


def accessiecodelijstmaker(file):
   count = 0
   accessionlist = []
   for item in file.readlines():
       list = item.split(",")
       if len(list) == 8:
           accessionlist.append(list[3 + 1].replace('\'', ''))
       elif len(list) == 9:
           accessionlist.append(list[5].replace('\'', ''))
       elif len(list) == 10:
           accessionlist.append(list[6].replace('\'', ''))
       elif len(list) == 11:
           accessionlist.append(list[7].replace('\'', ''))
       else:
           accessionlist.append(list[3].replace('\'', ''))

   return accessionlist


def refseqzoeker(accessiecodelijst):
   Entrez.email = "dit.wordt.mijn.spambox@gmail.com"
   for item in accessiecodelijst:
       print(item)
       handle = Entrez.efetch(db="protein", id=item, rettype="gb",
                             retmode="text")
       print(handle.readline().strip())



main()

