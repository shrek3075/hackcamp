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
    const { subject, testDate, startDate, busyDays, totalStudyHours, syllabusContent } = await req.json();
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY is not configured");
    }

    const systemPrompt = `You are an expert study planner. Create a detailed, day-by-day study plan based STRICTLY on the provided syllabus content.

CRITICAL: You MUST use ONLY the topics, concepts, and content from the syllabus provided by the user. Do NOT generate generic topics or add any topics not explicitly mentioned in the syllabus.

CRITICAL DATE RULES:
- The study plan MUST start on ${startDate} (this is TODAY - calculate the actual day of the week for this date)
- For ${startDate}, determine what day of the week it is (e.g., if it's 2025-11-16, that's a Sunday)
- Day 1 MUST have: date="${startDate}" and dayOfWeek="[correct day name for that date]"
- Each subsequent day must increment the date by 1 day in YYYY-MM-DD format
- Each date MUST have the correct corresponding dayOfWeek calculated from that date
- Skip any dates that fall on the busy days: ${busyDays.join(', ')} - when a date matches a busy day, skip to the next date
- The last study day should be BEFORE ${testDate} (test date)
- IMPORTANT: Calculate the actual calendar day of the week for each date - don't just cycle through day names

Your response MUST be a valid JSON object with this exact structure:
{
  "totalDays": number,
  "totalHours": number,
  "dailyPlans": [
    {
      "day": number,
      "date": "YYYY-MM-DD",
      "dayOfWeek": "Monday",
      "totalStudyHours": number,
      "sessions": [
        {
          "topic": "Topic name FROM THE SYLLABUS",
          "duration": number (in hours),
          "description": "What to focus on based on syllabus content",
          "priority": "high" | "medium" | "low"
        }
      ],
      "goals": "What to achieve this day based on syllabus"
    }
  ],
  "summary": "Brief overview of the plan with key milestones from the syllabus"
}

Important guidelines:
- ONLY use topics explicitly mentioned in the provided syllabus content
- Extract all topics, chapters, units, and subtopics from the syllabus
- Break down each study day into multiple focused sessions (2-4 topics per day)
- Assign specific time durations to each topic/session
- Distribute topics evenly across available study days
- Skip busy days (${busyDays.join(', ')}) - if a date falls on a busy day, skip to the next available day
- Distribute a total of ${totalStudyHours} hours across all study days (daily hours may vary)
- Start from ${startDate} (today) and work forward to ${testDate} (test date)
- ENSURE dates and dayOfWeek values match the actual calendar
- Include review sessions for previously covered syllabus topics before the test
- Mark urgent/important syllabus topics with high priority
- Break complex syllabus topics into manageable chunks
- Ensure ALL syllabus topics are covered with appropriate time allocation
- Add a final comprehensive review day before the test covering all syllabus content`;

    const userPrompt = `Create a study plan for:
Subject: ${subject}
Start Date: ${startDate} (TODAY - Day 1 of the plan)
Test Date: ${testDate}
Total Study Hours Available: ${totalStudyHours}
Busy Days (skip these): ${busyDays.join(', ')}

Syllabus Content:
${syllabusContent}

IMPORTANT: Start the plan from ${startDate} with the correct day of the week, and ensure all subsequent dates and days match the calendar. Generate a comprehensive day-by-day study timeline.`;

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
      
      // Check for token limit errors
      if (errorText.includes("maximum context length") || errorText.includes("tokens")) {
        return new Response(JSON.stringify({ error: "Your syllabus is too large. Please upload a shorter document or summary." }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      
      return new Response(JSON.stringify({ error: "Failed to generate study plan. Please try with a shorter syllabus." }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const data = await response.json();
    const planText = data.choices?.[0]?.message?.content || "No plan generated";
    
    // Try to parse JSON from the response
    let studyPlan;
    try {
      // Extract JSON from markdown code blocks if present
      const jsonMatch = planText.match(/```json\n([\s\S]*?)\n```/) || planText.match(/```\n([\s\S]*?)\n```/);
      const jsonStr = jsonMatch ? jsonMatch[1] : planText;
      studyPlan = JSON.parse(jsonStr);
    } catch (e) {
      console.error("Failed to parse JSON:", e);
      // Return raw text if JSON parsing fails
      studyPlan = { rawPlan: planText };
    }

    return new Response(
      JSON.stringify({ studyPlan }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error in generate-study-plan:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
