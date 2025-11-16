import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import "https://deno.land/x/xhr@0.1.0/mod.ts"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { messages, notes, planData } = await req.json()

    if (!messages || !Array.isArray(messages)) {
      return new Response(
        JSON.stringify({ error: 'Invalid request: messages array required' }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 400
        }
      )
    }

    const openAIApiKey = Deno.env.get('OPENAI_API_KEY')
    if (!openAIApiKey) {
      return new Response(
        JSON.stringify({ error: 'OpenAI API key not configured' }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 500
        }
      )
    }

    // Build context from selected notes
    let notesContext = ''
    if (notes && Array.isArray(notes) && notes.length > 0) {
      notesContext = '\n\nYou have access to the following study notes. Use these notes as reference to answer questions:\n\n'
      notes.forEach((note: any, index: number) => {
        notesContext += `--- Note ${index + 1}: ${note.title} (${note.subject}) ---\n${note.content}\n\n`
      })
      notesContext += '\nIMPORTANT: Use the information from these notes to help the student. If the question relates to topics in the notes, reference them in your answer.'
    }

    // Build context from study plan if provided
    let planContext = ''
    if (planData) {
      planContext = '\n\nThe student is currently working on the following study plan:\n\n'
      planContext += `Subject: ${planData.subject || 'Not specified'}\n`
      planContext += `Topic: ${planData.topic || 'Not specified'}\n`
      planContext += `Test Date: ${planData.test_date || 'Not specified'}\n`

      if (planData.plan_data?.dailyPlans) {
        planContext += '\nStudy Timeline:\n'
        const plans = planData.plan_data.dailyPlans.slice(0, 5) // Show first 5 days
        plans.forEach((day: any) => {
          planContext += `- Day ${day.day} (${day.date}): ${day.sessions?.map((s: any) => s.topic).join(', ') || 'No sessions'}\n`
        })
      }

      planContext += '\nUse this study plan context when helping the student with their learning.'
    }

    // Create system message for the tutor
    const systemMessage = {
      role: 'system',
      content: `You are a helpful and patient AI study tutor. Your role is to:
- Help students understand concepts clearly based on their study materials
- Break down complex topics into simple explanations
- Provide step-by-step guidance for problem-solving
- Encourage critical thinking rather than just giving answers
- Be supportive and encouraging
- Use examples and analogies to make concepts relatable
- Check for understanding and adjust your explanations accordingly
- When notes or study plans are provided, use them as context for your answers

${notesContext}${planContext}

Always be patient, clear, and encouraging. If a student is struggling, break things down further.${(notes && notes.length > 0) || planData ? ' Use the provided study materials and plan to give contextual, relevant help.' : ''}`
    }

    // Call OpenAI API
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openAIApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [systemMessage, ...messages],
        temperature: 0.7,
        max_tokens: 1000,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      console.error('OpenAI API error:', error)
      return new Response(
        JSON.stringify({ error: error.error?.message || 'Failed to get response from AI' }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: response.status
        }
      )
    }

    const data = await response.json()
    const aiResponse = data.choices[0]?.message?.content || 'I apologize, but I could not generate a response.'

    return new Response(
      JSON.stringify({ response: aiResponse }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200
      }
    )

  } catch (error) {
    console.error('Error in ai-tutor function:', error)
    return new Response(
      JSON.stringify({ error: error.message || 'Internal server error' }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500
      }
    )
  }
})
