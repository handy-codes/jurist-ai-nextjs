export type IncidentType = 'search' | 'arrest' | 'seizure' | 'assault' | 'other'

interface LawEntry {
  id: string
  title: string
  summary: string
  tags: string[]
}

const knowledgeByIncident: Record<IncidentType, LawEntry[]> = {
  search: [
    {
      id: 'const-37',
      title: 'Constitution of Nigeria 1999 - Section 37 (Right to Privacy) ',
      summary:
        'Protects the privacy of citizens, including homes, correspondence, telephone conversations and telegraphic communications.',
      tags: ['privacy', 'search', 'phones', 'devices']
    },
    {
      id: 'cpa-46',
      title: 'Criminal Procedure Act - Section 46 (Search Procedures)',
      summary: 'Provides lawful procedures for conducting searches and when they may be carried out.',
      tags: ['search', 'procedure', 'warrant']
    },
    {
      id: 'evidence-44',
      title: 'Evidence Act - Section 44 (Search Warrant Requirements)',
      summary: 'Sets out when a search warrant is required and how it should be issued.',
      tags: ['warrant', 'evidence']
    }
  ],
  arrest: [
    {
      id: 'const-35',
      title: 'Constitution of Nigeria 1999 - Section 35 (Right to Personal Liberty)',
      summary: 'Protects against unlawful detention and sets the rights of arrested persons.',
      tags: ['arrest', 'detention', 'rights']
    },
    {
      id: 'cpa-29',
      title: 'Criminal Procedure Act - Section 29 (Arrest Procedures)',
      summary: 'Outlines the manner of arrest and safeguards.',
      tags: ['arrest', 'procedure']
    }
  ],
  seizure: [
    {
      id: 'const-44',
      title: 'Constitution of Nigeria 1999 - Section 44 (Right to Property)',
      summary: 'Protects property rights and limits compulsory acquisition.',
      tags: ['property', 'seizure']
    },
    {
      id: 'cpa-44-seizure',
      title: 'Criminal Procedure Act - Section 44 (Seizure Procedures)',
      summary: 'Provides when and how items may be seized in investigations.',
      tags: ['seizure', 'procedure']
    }
  ],
  assault: [
    {
      id: 'const-34',
      title: 'Constitution of Nigeria 1999 - Section 34 (Right to Dignity)',
      summary: 'Prohibits torture and inhuman or degrading treatment.',
      tags: ['dignity', 'assault', 'force']
    },
    {
      id: 'cc-351',
      title: 'Criminal Code Act - Section 351 (Assault)',
      summary: 'Defines assault and sets penalties.',
      tags: ['assault', 'offence']
    }
  ],
  other: []
}

export function getApplicableLawTitles(incident: IncidentType): string[] {
  return (knowledgeByIncident[incident] || []).map((e) => e.title)
}

export function searchLawsByTags(incident: IncidentType, tags: string[]): string[] {
  const entries = knowledgeByIncident[incident] || []
  const results = entries.filter((e) => e.tags.some((t) => tags.includes(t)))
  return results.map((e) => e.title)
}
