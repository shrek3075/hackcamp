import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { notes, subject, syllabusContent, type } = await req.json();
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY is not configured");
    }

    // Handle flowchart generation
    if (type === 'flowchart') {
      const systemPrompt = `You are an expert educational content analyzer. Create a comprehensive mindmap/flowchart structure for the given subject and syllabus content.

Your response MUST be a valid JSON object with this exact structure:
{
  "subject": "subject name",
  "mainTopics": [
    {
      "name": "Main Topic Name",
      "description": "Brief description of this main topic",
      "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"]
    }
  ],
  "summary": "Brief overall summary of the content"
}

CRITICAL INSTRUCTIONS:
1. Extract ONLY topics that appear in the provided syllabus content
2. Organize topics hierarchically - identify 4-6 main topics and their subtopics
3. Each main topic should have 3-6 relevant subtopics
4. Keep topic names concise and clear
5. Ensure all topics are directly from the syllabus content
6. DO NOT generate generic topics - use ONLY what's in the syllabus
7. Return ONLY the JSON object, no additional text`;

      const userPrompt = `Subject: ${subject}

Syllabus Content:
${syllabusContent || 'No syllabus content provided'}

Create a mindmap structure with main topics and subtopics based on the above syllabus content.`;

      console.log("Generating flowchart for subject:", subject);

      const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${LOVABLE_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "google/gemini-2.5-flash",
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userPrompt }
          ],
          temperature: 0.7,
        }),
      });

      if (!response.ok) {
        if (response.status === 429) {
          return new Response(JSON.stringify({ error: "Rate limits exceeded, please try again later." }), {
            status: 429,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
        if (response.status === 402) {
          return new Response(JSON.stringify({ error: "Payment required, please add funds to your Lovable AI workspace." }), {
            status: 402,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
        const errorText = await response.text();
        console.error("AI gateway error:", response.status, errorText);
        throw new Error(`AI gateway returned status ${response.status}`);
      }

      const data = await response.json();
      const content = data.choices?.[0]?.message?.content;

      if (!content) {
        throw new Error("No content received from AI");
      }

      console.log("Raw AI response:", content);

      // Extract JSON from markdown code blocks if present
      let jsonContent = content.trim();
      if (jsonContent.startsWith("```json")) {
        jsonContent = jsonContent.replace(/^```json\s*/i, "").replace(/```\s*$/i, "");
      } else if (jsonContent.startsWith("```")) {
        jsonContent = jsonContent.replace(/^```\s*/, "").replace(/```\s*$/i, "");
      }

      const flowchart = JSON.parse(jsonContent);

      return new Response(JSON.stringify({ flowchart }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Handle study recommendations (original functionality)
    const notesContext = notes
      .map((note: any) => `Title: ${note.title}\nContent: ${note.content}`)
      .join('\n\n');

    const systemPrompt = `You are an expert study advisor. Based on the student's notes, provide personalized study recommendations to help them prepare effectively for their exam.

Focus on:
1. Key topics they should prioritize based on their notes
2. Areas that might need more attention or review
3. Practical study techniques for the specific content
4. Time management suggestions

Keep recommendations concise, actionable, and specific to the notes provided.`;

    const userPrompt = `Here are the student's notes for ${subject}:

${notesContext}

Please provide 3-5 specific study recommendations to help them prepare for their ${subject} exam.`;

    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt },
        ],
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(JSON.stringify({ error: "Rate limits exceeded, please try again later." }), {
          status: 429,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      if (response.status === 402) {
        return new Response(JSON.stringify({ error: "Payment required, please add funds to your workspace." }), {
          status: 402,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      const errorText = await response.text();
      console.error("AI gateway error:", response.status, errorText);
      return new Response(JSON.stringify({ error: "AI gateway error" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const data = await response.json();
    const recommendations = data.choices?.[0]?.message?.content || "No recommendations generated";

    return new Response(
      JSON.stringify({ recommendations }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error in generate-study-recommendations:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
