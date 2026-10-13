# AI Prompts

This file preserves the prompts and follow-ups in chronological problem order.

## Problem 1 — Campus Customs multi-agent operations

### Raw prompt

Hi there, we will be starting homework 5. We'll be working in HW 5 folder in _AI folder in my documents. We will be working on our campus customs multi-agent operations, an agentic team that runs our shop. It should handle open tickets on a board, including customer orders, rent, unpaid, bills, discount requests, and whatever other misc the shop has to handle. There will be 3 components all talking to each other: 1. MCP server 2. FastAPI backend w multi-agent team 3. React dashboard so I can watch agents work and approve requests. Agent team must ahve full connectivity, meaning an agent can delegate tasks to any other agent. We will have the following agents in the assignment: 1. Boss: reads ticket, delegates work, makes final decision 2. Inventory: checks stock by SKU & size, spots shortfalls, decides which vendor will restock 3. Accounting: monitors cash & invoices, reviews margins, prepares payments or PO for my approval 4. Facilities: handles shop space (leases, rent, etc) 5. Customer service: writes messages for customers. Don't respond yet, just read adn go to the hw 5 folder

### Project context

ok, project context: data is in campus customs db. As tickets get resolved, you will updat ethe db. there is a copy called campus_customs_new.db and the MCP server & BE should point to that working copy. campus_customs will be untouched so we can reset when we want to restart resolving tickets. Requirements: 1. Field 'desk.date_today' is 'today' for shop. Use this date for evaluating overdue 2. Vendor lead times = vendors table 3. Vendor won't ship new product while there's an open unpaid invoice 4. my approval is required for any payments. THIS IS ESSENTIAL. If payment is made, it needs to be updated in the relevant table. 5. If there is insufficient cash, pay tool MUST refuse. under any circumstances, NO NEG BALANCES. 6. Cash only goes out in this hw. We don't model revenue, so no money comes in 7. Before full run to resolve tix, make sure to reset the DB to original values 8. DO NOT EMAIL OR CALL real vendors. Drafts ALL STAY ON BOARD ONLY. 9. Portkey api key is used for AI calls.ONLY gpt-6-luna is allowed, nothing stronger. Let me know when you've read and understood project context b4 i continue

Problem 1: Remember, for all HW, create AI_prompts.md to store my raw prompts, each problem number/title, and any follow-up.

## Problem 2 — Study Campus Customs Database

### Raw prompt

Problem 2: Study Campus Customs Database. Open campus_usstoms.db and look through all the tables/fields. The copy 'campus_customs_new' will be updated in later problems as a working copy. Study the 3 open tix so you see how they link to other tables. Please start 'output/harness.md'. For each table, list fields and a short line on why that table matters for the agents. Keep growing this file in later problems.

## Problem 3 — Build MCP Server

### Raw prompt

Problem 3: Build MCP Server. Write an mcp server in mcp_server/ using FastMCP. It will talk to data/campus_customs_new.db. Do NOT connect or run it in this problem. Every agent in this hw uses tools in this mcp server. Later, we'll add more tools so for now just write 3 tools you know you'll need for tex in the db. Keep names clear, never invent or hallucinate data, only use info in the db. ask me i fyou get confused. Ok next, in output/harness.md, liste each of the 3 mcp tools. Make sure you include: which table tool reads, which ticket it helps unlock (101/102/103) and one setnece ONLY on why that tool is right for that ticket. You cannot use vague setnences like 'reads inventory'. the tool must be specifically tied to the ticket with a clear explanation. Add a short mcp_server/README.md file explaining the above (what mcp server is for, which db file it uses, and 3 tools it has)

## Problem 4 — Add MCP server to vibe coder and test each tool

### Raw prompt

Problem 4: Add MCP server to vibe coder & test each tool. Let's now add the mcp server to this project so we can call tools. Save connection JSON text in .mcp.json at the proejct root. After it's connected, test EACH of the 3 mcp tools. Make sure evidence is saved in output/mcp_smoke.json. make sure every tool has: 1. prompt asked of the vibe coder 2. tool name 3. tool output (values must match waht's in data/campus_customs_new.db).

## Problem 5 — Build agent team and grow MCP tools

### Raw prompt

Problem 5: build agent team & grow MCP tools. Let's now build agentic team for campus customs using pydanticAI and the 5 agent categories described in project context. Include prompts, models, and agent loops so work can be delegated amongst agents w full connectivity. Place agent prmpts in backend/prompts/ with one file per agent. Put data types in backend/models.py and agent files in backend/ (layout can vary as long as 5 roels are clear). Use portkey api key and only luna per project context. Write each prompt in own words with shop rules the agent will need. More detailed prompts covering all aspects of work and scope are much more valuable to me than short/generic. Any tools the agent needs should be added to the mcp server so they can work on open tix. Shop facts will come form the mcp server over data/campus_customs_new.db. Make sure NOT to invent a second shop-tools layer that bypasses mcp. Wire agents so they are appended to output/audit_trail.json as they run. For each agent-loop step, record enough to aduti later. Append to this file and don't wipe it each run. In output/harness.md, list each agent and each mcp tool (including ones we add in this problem) along with which table the tool uses. Add a short safety section, bc we need guardrails that a real business would want when agents touch real customers and real money, plus limits keeping our token use in check. More detail: do not transfer any money if not explicitly dictated. Do not share or transfer any financial information or secure data like card numbers, account numbers, etc. Flag any transactions over $1000. Update mc-Pserver/README.md so tool list matches what you have now.

## Problem 6 — Plan the three tickets

### Raw prompt

Problem 6: plan the 3 tickets. Before wiring BE, write down what you expect the team to do for each open ticket. Create output/desk_tickets.html, a site we can double-click with one tab per ticket (101/102/103). Add empty Cash and Reflection tabs as placeholders for later porlbmes, you can add 'in construction' note for now. On each ticket tab, complete an Expected section only but leave room for an Actual section we will fill after the agents run. For each Expected section, write in own words: 1. Who Boss should call first and why 2. All agent delegations we expect (can't be "Boss calls on everyone) 3. Which MCP tools are expected that run to use. Do not send every specialist on every ticket. We want ti specialize / segment. Compare this plan to what happens when agents resolve the 3 tickets. Ask me for my input on key decisions you're making for the expected section.

### Follow-ups

what are other possible orders you could follow to give me a comparison for decision making?

why would we jump to accounting before confirming we have something in inventory? please justify more for ticket 101 why inventory first is an alt order and not your current first call. Becuase then for ticket 103 you put inventory first as the default

ok yes let's do inventory first. do you now have all you need to complete problem 6?

ok anything else you need or want clarification on to make our Expected stronger?

1 return to boss 2. leave open when awaiting approval 3. recommendation is fine and then po generated once approval is complete

I reviewed desk_tickets.html. I'm not seeing a bulldog anywhere. I'm not seeing any prodcut pictures anywhere. For example ticket 101: Ticket 101 · Bulldog tee / Tauhid Zaman · one `CC-TEE-WHITE` this gives me no understanding of what this prodcut is. In HW 4 we used product images so you still have access to that. Also for delegtaion sequence make this more creative/ interactive looking

Classic Bulldog Tee has incorrec timage in ticket 101. you can find more images at the campus custom website, for example I searched classic bulldog tee here: 'https://yalebulldogblue.com/search?q=classic+bulldog+tee'. also, Expected should have sentence description that describes full process not just what the Boss Calls First. Delegation sequence can stay a sumlmarized graphic as you have it currently. The icon in the top left of the website is not actuallly a bulldog it looks liek a sheep. attached is a photo of the original bulldog mascot

now just edit the bulldog in the top left. just make it this picture

stop searching for other photos the webpage should use the one i gave you hard stop. The product photos are good so no more searching, just use this and finish.

## Problem 7 — Backend Routes

### Raw prompt

Problem 7: Backend Routes. Our react FE dashboard in our following problem needs a BE at backend/main.py. Use FastAPI and add routes for: 1. Return 3 tix and whether each is open or resolved 2. take ticket id and run agent team on ticket 3. Return recent agent events (what agent said & tools used) so board can refresh 4. Approve payment/purchase after human clicks approve (agents only prepare pay, this route is what changes cash) 5. Return current checking balance from cash_accounts 6. Reset DB to original values when we want a fresh run 7. From backend/ folder, start server with: uvicorn main:app --reload --port 8000. List each route in one lien (URL and what it does) in output/harness.md

## Problem 8 — Agent dashboard

### Raw prompt

Problem 8: agent dashboard. Build FE in frontend/ with React + Vite + Typescript. Page should call routes from problem 7. At a min board should: 1. list all 3 tix 2. let me pick 1 ticket and start agent team on it 3. show each agent and what they're saying/doing while ticket runs 4. mark resolved when run completes 5. show short summary of what each agent did on the ticket 6. let human approve a pay or purchase when asked 7. show checking balance. note it should drop after an approved pay. NOTES: make the dashboard look great! feel free to be creative with layout and feel. We want this to be a real desk people want to sit at. Use Yale colors, make a bulldog logo somewhere in the website. Make sure FE talks to BE at http://localhost:8000. On BE allow Vite page origin http://localhost:5173 so browser can call those routes. Start board with: npm run dev write output/design.md with what you chose for dashboard look (layout, how agent reads differently, how resolved tix and cash appear) and why. Include creativity choices that are SPECIAL. if you need help, lmk

### Follow-ups

if i try to run that batch it says "ENOENT: no such file or directory: frontend"

if i run the backend it gives error: 'ERROR: [Errno 48] Address already in use'

still getting address in use even when quitting out of terminal

still getting same even after running both commands

describe how i approve in the FE and give a recommendation as to whether or not i should approve each ticket

go back to the original project context: vendor will not ship new product while they still have na open unpaid invoice, and if there is not enough cash, the pay tool must refuse - no negative balances. Cash only goes out, no money comes in. before full run to resolve tickets, the database must be reset to original values. According to those principles, how should i proceed in the fe approval process?

so these are the things that you should be doing haha like I'm not doing any database resets or anything like that. So let's assume you're right on all fronts, tell me what to do next to complete this assignment

wait I still want to be able to do human approvals on the FE. that'salso a requirement remember? But i'm not resetting database

what is up with the 'reference' field?

ok first 2 tickets were approved adn resolved, running agent for 103. team is working on perpetual loop, please kill and investigate

no you will please test the backend and when you confirm it's now working I will re-run agent team in FE for 103

i'm not seeing facilities triggered for ticket 103, what's happening?

ok ticket 103 ran successfully this time. no wwhat should i do for the approval?

the agents should be flagging this for me, update so that this happens inherently in our flow for the human approver to review

how do i restart be?

still getting address in use even after running both commands

on emoment: in the instructions it says run all 3 tickets on the board until each is resolved. so how do we do that for ticket 103?

remind me how to restart fe

## Problem 9 — Resolve the tickets

### Raw prompt

Problem 9: Resolve the tickets. Before we test agents on a full run over 3 tix, reset working database data/campus_customs_new.db so we start fresh. Note starting checking balance and tell me what it is. Then run all 3 tix on the board until each is resolved. Open the desk tix html. On each ticket tab, enter in the Actual section from this run. Make sure to include: 1. which agents worked 2. what they delegated 3. which tools they used. Keep the expected section so we can compare. On Cash tab, itemize the money: 1. Starting checking balance after reset 2. For each ticket, how cash changed when ticket resolved and why (which pay/purchase, dollar maount), and ending checking balance (must match cash_accounts in the working database). Wrong cash math loses points even if board lists every resolved ticket. Also save output/resolved_tickets.json fore each ticket: id, final status, short outcome, what each agent contributed, human approvals. Also save output/resolved_board.html: page you can double-click with a screenshot of react board for each resolved ticket. Append real runs to output/aduit_trail.json. Complete output/harness.md so it has tables, mcp tool,s 5 agents, api routes, dashboard, adn safety rules

### Follow-ups

pause. I will tell you when to resume. just need to run an errand

ok I'm back, please resume. thanks!

wait why are you using openAImodel we have the portkey api key we've been using this whole time together

ok thanksf or clarifying. please continue

is there a way to integrate this decision making into the front end? just say yes or no before proceeding

another way of asking: can I have a user make deicions through the html front end or do I have to speak only through our chat here

ok let's do it! please proceed with this

i don't see anywhere to approve in the desk_tickets html. please clarify

ok first 2 tickets were approved adn resolved, running agent for 103. team is working on perpetual loop, please kill and investigate

the agents should be flagging this for me, update so that this happens inherently in our flow for the human approver to review

what is up with the 'reference' field?

ok resolved all in FE. Please finish Problem 9

teh 'actual completed' section is not detailed enough. tell me more about the granular details of what happened when this ran in terms of what the agents were doing, how they talked to each other and the boss

i'm reading ticket 101 and not understanding. how did we fulfill the order if we had no item in the inventory?

wait but would we want to approve at all if we have no inventory?

### Clarification about resolution

raed the instructions again and tell me what the definition of resolved is in this assignment

ok let's leave as is then.

## Problem 10 — Reflection

### Raw prompt

Problem 10: Reflection. We will need to fill in the Reflection tab of desk_tickets with the following. inlcude your thoughtful first pass at answers. I'll edit it, give it back to you, and have you update the html. 1. How would you evaluate performance of the agents on each ticket and why? 2. for each ticket how did actual compare to expected plan you wrote earlier? 3. what would have been simpler as one agent with tools - and why? 4. Describe 3 new problems Campus Customs might face that his agent team could sove with the tools you built 5. Describe 3 new problemsCC might face that this agent team could NOT solve with the tools you bilt and explain tools/agents you woul dneed to sovle them. Tie every answer to this app and the 3 tix ran - use tix tabs and cash tab on same page as evidence. Generic AI essays w/o campus customs details will score low.

### Review follow-ups

you misread. i told you we'd create the template first BEFORE updating the html, but oh well. 1 Ticket 101: Generally speaking, the agent completed tasks as asked. It didn't think about what having no inventory meant in the broader context of the shop. We can't fulfill an order if something isn't in inventory. After going back and forth, the assignment didn't define this as a limitation to fulfilling an order, so I still approved, but I think the agent should have flagged that in inventory to start. Ticket 102: The agents got muddled with the role of Facilities and treated it as obsolete. However, their answer/outcome was correct, so I disregarded the error. I had put in a clause about flagging high orders over $1k so it did flag that without stopping the full flow. Ticket 103: the system did a good job observing the no negative cash balance rule and appropriately flagged it when it occurred. It was unclear from a human approver standpoint, however, as to what to do and how to navigate through the website once this was flagged, so it was frustrating trying to figure this out. For 2 don't really have anything to add. For 3 add that 5-agent is also much more convenient for troubleshooting. Talk about whether or not you would consolidate down so that it's still a bit easier to troubleshoot but also makes more intuitive sense for handling tasks. For 4 the 3 new problems these don't really make sense to me so try to come up with 3 that are very simple and easy to read in natural human language. For 5 #1 don't love this example keep it something more human oriented. For 2 and 3 talk about the social and mental component of customers having an easier time reasoning with a human and giving them that personalized experience when there's some kind of issue that they're looking. The evidence section doesn't make any sense either clarify or remove. Just give me the text back in this chat don't update html yet so i can look and approve before wasting tokens on html updates

your ticket 103 is bad you removed a lot of detail. It didn't 'feel' like perpetual loop it did get stuck over and over and we had to spend time troubleshooting. add back my original text for it as well to fully explain the trouble with being able to move forward after it was flagged. For 5 header remove 'genuinely'. Also 1-3 now all sound exactly the same because you oversantiized them. they need to be more distinct

new problems 1 and 3 are still basically the same. fix

personalized si the same as personal exception. think bigger like having some kind of automated big money thing happening is also obviously scary or infringing on sensitive data is scary so yolu can go that route for one of these

ok great now output everything again for my final review / approve

great last request just remove colons from the text or super AI-y fomratting

### Final follow-ups

great! update html now

ok great! make final changes to the prompt file to account for our work

this prompt file doesn't make sense, it needs to go in order from problems 1-10 and encompass all of the prompts I gave you. i'm seeing a lot of summarization and not my conversations with you
