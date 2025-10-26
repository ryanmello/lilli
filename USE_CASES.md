# 📋 Bloomer Agent - Use Cases & User Stories

This document provides detailed use cases and user stories to illustrate how the Bloomer Agent system handles various flower shop scenarios.

---

## Table of Contents

1. [Simple Inventory Queries](#simple-inventory-queries)
2. [Order Management](#order-management)
3. [Customer Service](#customer-service)
4. [Floral Design Consultation](#floral-design-consultation)
5. [Delivery Management](#delivery-management)
6. [Complex Multi-Agent Scenarios](#complex-multi-agent-scenarios)
7. [Error Handling Scenarios](#error-handling-scenarios)

---

## Simple Inventory Queries

### Use Case 1.1: Basic Stock Check

**User Story**: As a shop employee, I want to quickly check if we have specific flowers in stock.

**Query**: "Do we have red roses?"

**Workflow**:
```
1. Orchestrator receives query
2. Classifies as: inventory_check (confidence: 0.95)
3. Extracts entities: {flower: "rose", color: "red"}
4. Routes to: Inventory Agent
5. Agent calls: check_stock("rose", "red")
6. Returns: "Yes, 150 stems available"
7. Response synthesized and displayed
```

**Expected Response**:
```
Yes, we have 150 stems of red roses in stock. They're fresh (received 
yesterday) and in excellent condition. Would you like to create an order?
```

---

### Use Case 1.2: Multi-Variant Inventory Check

**User Story**: As a shop employee, I want to see all available variants when checking stock.

**Query**: "What roses do we have?"

**Workflow**:
```
1. Orchestrator classifies: inventory_check
2. Routes to: Inventory Agent
3. Agent calls: search_inventory({"type": "rose"})
4. Returns all rose variants with quantities
```

**Expected Response**:
```
We currently have the following roses in stock:

• Red Roses: 150 stems ($2.50/stem)
• White Roses: 80 stems ($2.75/stem)  
• Pink Roses: 120 stems ($2.50/stem)
• Yellow Roses: 95 stems ($2.50/stem)
• Peach Roses: 45 stems ($3.00/stem)

All are fresh with a freshness rating of 9/10.
```

---

### Use Case 1.3: Low Stock Alert

**Query**: "What flowers are running low?"

**Workflow**:
```
1. Orchestrator classifies: inventory_check (low_stock)
2. Routes to: Inventory Agent
3. Agent calls: get_low_stock_items(threshold=50)
4. Returns items below threshold
```

**Expected Response**:
```
The following items are running low:

⚠️  Peach Roses: 45 stems (reorder threshold: 50)
⚠️  White Lilies: 30 stems (reorder threshold: 50)
⚠️  Sunflowers: 25 stems (reorder threshold: 40)

Would you like me to calculate reorder quantities?
```

---

## Order Management

### Use Case 2.1: Simple Order Creation

**User Story**: As a customer, I want to place a simple flower order.

**Query**: "I want to order 2 dozen red roses"

**Workflow**:
```
1. Orchestrator classifies: order_creation
2. Routes to: Order Agent
3. Agent extracts: 24 red roses
4. Calls: calculate_pricing(items)
5. Prepares order summary
```

**Expected Response**:
```
Perfect! Here's your order summary:

Order Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 24 Red Roses          $60.00
• Arrangement/Wrapping   $8.00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Subtotal:             $68.00
  Tax (8%):              $5.44
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total:                $73.44

To proceed, I'll need:
1. Delivery or pickup?
2. Your contact information
3. Delivery address (if applicable)
4. Any special instructions

Would you like to continue with this order?
```

---

### Use Case 2.2: Order Tracking

**User Story**: As a customer, I want to check the status of my existing order.

**Query**: "What's the status of order #12345?"

**Workflow**:
```
1. Orchestrator classifies: order_tracking
2. Extracts entity: order_id = "12345"
3. Routes to: Order Agent
4. Agent calls: get_order_status("12345")
5. Returns detailed order information
```

**Expected Response**:
```
Order #12345 Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: Out for Delivery 🚚
Expected Delivery: Today, 2:00 PM - 4:00 PM

Order Details:
• 24 Red Roses
• Wedding Bouquet Arrangement
• Ordered: Oct 25, 2025

Delivery Address:
123 Main Street, Los Angeles, CA 90210

Tracking: Your order is with driver Maria and is 
currently 3 stops away from your location.

Need to make changes? Let me know!
```

---

### Use Case 2.3: Order Modification

**Query**: "Can I add white lilies to order #12345?"

**Workflow**:
```
1. Orchestrator classifies: order_modification
2. Routes to: Order Agent
3. Agent retrieves order details
4. Checks order status (must be modifiable)
5. Validates lily availability (calls Inventory)
6. Calculates new pricing
```

**Expected Response**:
```
I can help modify order #12345!

Current Status: Confirmed (can be modified)

How many white lily stems would you like to add?
We currently have 80 stems available at $3.50/stem.

Note: Adding items may affect delivery time and cost.
```

---

### Use Case 2.4: Order Cancellation

**Query**: "I need to cancel order #12345"

**Workflow**:
```
1. Orchestrator classifies: order_cancellation
2. Routes to: Order Agent
3. Agent validates cancellation eligibility
4. Processes cancellation
5. Initiates refund process
```

**Expected Response**:
```
I can help you cancel order #12345.

Order Details:
• 24 Red Roses - $73.44
• Status: Confirmed
• Scheduled Delivery: Tomorrow, 2:00 PM

Cancellation Policy:
✓ Full refund available (order not yet in progress)
✓ Refund will be processed in 3-5 business days

To confirm cancellation, please type: "CONFIRM CANCEL"

Or if you'd like to modify instead of cancel, I can help with that too!
```

---

## Customer Service

### Use Case 3.1: Flower Care Instructions

**User Story**: As a customer, I want to know how to care for my flowers.

**Query**: "How do I care for roses?"

**Workflow**:
```
1. Orchestrator classifies: customer_question (flower_care)
2. Routes to: Customer Service Agent
3. Agent retrieves care instructions from knowledge base
```

**Expected Response**:
```
Here's how to care for your roses to keep them fresh:

🌹 Rose Care Guide:

1. Water:
   • Use clean, cool water
   • Change water every 2-3 days
   • Add flower food if provided

2. Trimming:
   • Cut stems at 45° angle
   • Remove 1-2 inches from bottom
   • Re-cut every few days
   • Remove any leaves below water line

3. Placement:
   • Keep away from direct sunlight
   • Avoid heat sources and drafts
   • Room temperature is ideal (65-72°F)

4. Maintenance:
   • Remove wilted petals promptly
   • Keep vase clean
   • Mist petals lightly (optional)

Expected Lifespan: 7-12 days with proper care

Pro Tip: Add a penny to the water to help prevent bacteria!

Need any other care tips?
```

---

### Use Case 3.2: Occasion Recommendations

**Query**: "What flowers are good for an anniversary?"

**Workflow**:
```
1. Orchestrator classifies: customer_question (recommendation)
2. Routes to: Customer Service Agent + Design Agent
3. Agents collaborate on recommendations
```

**Expected Response**:
```
Great question! Here are the best flowers for anniversaries:

🌹 Classic Anniversary Flowers:

1. Red Roses - Traditional choice
   • Symbolize deep love and passion
   • Perfect for romantic anniversaries
   
2. Carnations - By year
   • Different colors for different anniversary years
   • Traditional anniversary flower
   
3. Calla Lilies - Elegant choice
   • Represent devotion and marital bliss
   • Sophisticated and modern

🎨 Color Meanings:
• Red: Passionate love
• Pink: Grace and admiration  
• White: Purity and unity
• Yellow: Friendship and joy

💡 Our Recommendations:
• 1st Anniversary: White carnations or roses
• 10th Anniversary: Traditional - Daffodils
• 25th Anniversary: Iris flowers
• 50th Anniversary: Yellow roses or violets

Would you like help designing a custom anniversary arrangement?
```

---

### Use Case 3.3: Flower Meanings

**Query**: "What do sunflowers symbolize?"

**Workflow**:
```
1. Orchestrator classifies: customer_question (flower_meaning)
2. Routes to: Customer Service Agent
3. Agent retrieves symbolic meanings
```

**Expected Response**:
```
Sunflowers have beautiful and uplifting symbolism:

🌻 Sunflower Meanings:

Primary Symbolism:
• Adoration and loyalty
• Happiness and positivity
• Longevity and lasting happiness
• Dedication and devotion

Cultural Significance:
• Native American: Harvest and provision
• Chinese: Long life and good luck
• General: Following your truth (like they follow the sun)

Perfect For:
✓ Get-well wishes
✓ Congratulations
✓ Friendship celebrations
✓ Third wedding anniversary
✓ Brightening someone's day

Fun Fact: Sunflowers are known for their "heliotropism" - 
young sunflowers track the sun's movement across the sky!

Would you like to order sunflowers for someone special?
```

---

### Use Case 3.4: Store Information

**Query**: "What are your store hours?"

**Workflow**:
```
1. Orchestrator classifies: customer_question (store_info)
2. Routes to: Customer Service Agent
3. Agent retrieves store information
```

**Expected Response**:
```
Bloomer Flower Shop - Store Information

📍 Location:
123 Flower Street
Los Angeles, CA 90210

⏰ Store Hours:
Monday - Friday:    9:00 AM - 7:00 PM
Saturday:          8:00 AM - 8:00 PM  
Sunday:           10:00 AM - 6:00 PM
Holidays:          10:00 AM - 4:00 PM

📞 Contact:
Phone: (555) 123-4567
Email: hello@bloomershop.com

🚚 Delivery Available:
Same-day delivery for orders placed before 2:00 PM
Free delivery on orders over $75

Is there anything else you'd like to know?
```

---

## Floral Design Consultation

### Use Case 4.1: Wedding Bouquet Design

**Query**: "Design a wedding bouquet with roses and lilies"

**Workflow**:
```
1. Orchestrator classifies: design_request (wedding)
2. Routes to: Design Agent
3. Agent considers: occasion, flowers, style
4. Creates custom design
5. Calculates needed quantities
```

**Expected Response**:
```
I'd love to design a wedding bouquet for you! Here's a beautiful concept:

💐 Elegant Rose & Lily Bridal Bouquet

Design Concept:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Style: Classic Romance with Modern Elegance

Flowers:
• 18 White Roses - Purity and new beginnings
• 6 White Calla Lilies - Magnificent beauty
• 12 White Spray Roses - Delicate accents
• Baby's Breath - Filler for fullness
• Eucalyptus - Greenery and texture

Color Palette:
• Primary: Pure White
• Accents: Soft Green (eucalyptus)
• Ribbon: Ivory satin

Size: Medium (12" diameter, 14" length)

Design Features:
✓ Cascading style with natural flow
✓ Hand-tied with exposed stems
✓ Wrapped in ivory satin ribbon
✓ Finished with pearl pins

Estimated Cost: $185.00

Matching Options Available:
• Bridesmaids' bouquets (smaller version) - $75 each
• Boutonnieres - $15 each
• Centerpieces - $95 each

Would you like to:
1. Proceed with this design?
2. Adjust flowers or colors?
3. See alternative styles?
```

---

### Use Case 4.2: Color Palette Suggestions

**Query**: "What colors go well with lavender?"

**Workflow**:
```
1. Orchestrator classifies: design_request (color_consultation)
2. Routes to: Design Agent
3. Agent uses color theory knowledge
```

**Expected Response**:
```
Lavender is a beautiful, versatile color! Here are complementary palettes:

🎨 Color Combinations with Lavender:

1. Classic & Romantic:
   • Lavender + White + Silver
   • Perfect for: Weddings, formal events
   • Flowers: Lavender roses, white lilies, silver brunia

2. Soft & Dreamy:
   • Lavender + Blush Pink + Cream
   • Perfect for: Baby showers, spring events
   • Flowers: Lavender stock, pink roses, cream ranunculus

3. Bold & Modern:
   • Lavender + Deep Purple + Plum
   • Perfect for: Contemporary settings
   • Flowers: Lavender carnations, purple lisianthus, plum dahlias

4. Garden Fresh:
   • Lavender + Yellow + Green
   • Perfect for: Casual, cheerful arrangements
   • Flowers: Lavender, sunflowers, greenery

5. Elegant & Sophisticated:
   • Lavender + Grey + White
   • Perfect for: Corporate events, modern weddings
   • Flowers: Lavender roses, white hydrangeas, dusty miller

💡 Pro Tips:
• Use white to make lavender pop
• Add greenery for natural balance
• Silver accents enhance the ethereal quality

What type of event or arrangement are you planning?
```

---

### Use Case 4.3: Seasonal Arrangements

**Query**: "Show me fall arrangement ideas"

**Workflow**:
```
1. Orchestrator classifies: design_request (seasonal)
2. Routes to: Design Agent
3. Agent retrieves seasonal templates
4. Considers current inventory
```

**Expected Response**:
```
Beautiful fall arrangements coming up! 🍂

🍁 Fall Floral Design Ideas:

1. "Autumn Harvest" Centerpiece
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • Orange roses and gerbera daisies
   • Burgundy chrysanthemums
   • Sunflowers (smaller varieties)
   • Wheat stalks and dried leaves
   • Rustic basket or wooden box
   Price: $85 | Size: Large
   
2. "Pumpkin Spice" Arrangement
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • Burnt orange carnations
   • Yellow button mums
   • Deep red spray roses
   • Miniature pumpkin vase
   • Cinnamon sticks accent
   Price: $65 | Size: Medium

3. "Forest Floor" Design
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • Burgundy dahlias
   • Chocolate cosmos
   • Rust-colored hypericum berries
   • Pine cones and moss
   • Natural wood container
   Price: $95 | Size: Large

4. "Thanksgiving Table Runner"
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • Assorted fall flowers
   • Floating candles
   • Seasonal foliage
   • Decorative gourds
   • 24" length arrangement
   Price: $125

Color Palette: 
🎨 Orange, Burgundy, Gold, Rust, Deep Yellow

Available Add-ons:
• Scented elements (cinnamon, pine)
• LED candles
• Seasonal ribbons

Would you like to order one of these, or create a custom fall design?
```

---

## Delivery Management

### Use Case 5.1: Delivery Availability Check

**Query**: "Can you deliver to 90210 tomorrow?"

**Workflow**:
```
1. Orchestrator classifies: delivery_inquiry
2. Extracts: zip_code = "90210", date = "tomorrow"
3. Routes to: Delivery Agent
4. Agent calls: check_delivery_availability("90210", tomorrow_date)
```

**Expected Response**:
```
Yes, we can deliver to 90210 tomorrow! 

Delivery Options for ZIP 90210:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Standard Delivery:
• Time Window: 9:00 AM - 6:00 PM
• Fee: $12.00
• Earliest: Tomorrow

Express Delivery:
• Time Window: You choose specific 2-hour window
• Fee: $25.00  
• Earliest: Tomorrow, 10:00 AM

Same-Day Rush:
• Available if ordered before 12:00 PM today
• Fee: $35.00
• Delivery by: 6:00 PM today

📦 Delivery Area: Beverly Hills and surrounding areas
🎯 Delivery Success Rate: 99.2% on-time

Notes:
• Signature required for orders over $100
• We'll call recipient 30 minutes before delivery
• Real-time tracking available via SMS

Would you like to schedule a delivery?
```

---

### Use Case 5.2: Delivery Tracking

**Query**: "Where is my delivery?"

**Workflow**:
```
1. Orchestrator classifies: delivery_tracking
2. Routes to: Delivery Agent
3. Agent needs order identification
4. Prompts for order number or asks for recent orders
```

**Expected Response**:
```
I can help you track your delivery!

I found a recent delivery associated with your account:

🚚 Delivery for Order #12345
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current Status: Out for Delivery
Driver: Maria Rodriguez
Vehicle: Van #7

🗺️  Live Tracking:
Current Location: 3 stops away
Estimated Arrival: 2:30 PM - 3:00 PM (in ~45 minutes)

Route Progress:
✓ Departed facility (10:15 AM)
✓ Stop 1 completed (11:00 AM)
✓ Stop 2 completed (12:30 PM)
✓ Stop 3 completed (1:45 PM)
→ Your location next

Delivery Address:
123 Main Street, Los Angeles, CA 90210

📱 We'll send you an SMS when the driver is 10 minutes away.

Need to change delivery instructions? Let me know!
```

---

### Use Case 5.3: Special Delivery Requests

**Query**: "I need flowers delivered at exactly 2pm for a surprise"

**Workflow**:
```
1. Orchestrator classifies: delivery_inquiry (special_request)
2. Routes to: Delivery Agent
3. Agent checks scheduling capabilities
4. Validates timing and calculates fees
```

**Expected Response**:
```
I can absolutely help coordinate a surprise delivery! 🎉

Precision Delivery Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Requested Time: 2:00 PM
Service Type: Timed Delivery (±15 minutes)
Additional Fee: $15.00

How it Works:
1. We schedule delivery for 1:45 PM - 2:15 PM window
2. Driver calls you 30 minutes before arrival
3. We coordinate to arrive at your specified time
4. Discreet delivery - no company logos if requested

Special Instructions Options:
□ Call recipient first (or skip for surprise)
□ Hide company branding
□ Specific delivery location (front door, office reception, etc.)
□ Photo confirmation after delivery
□ Custom delivery note instructions

💡 Pro Tips for Surprise Deliveries:
• Confirm recipient will be present
• Provide alternative contact if needed
• Consider indoor/outdoor placement
• Weather protection if left outside

What's the delivery address and any special instructions?
```

---

## Complex Multi-Agent Scenarios

### Use Case 6.1: Complete Order with Design and Delivery

**User Story**: As a customer, I want to order a custom arrangement with delivery in one conversation.

**Query**: "I need a birthday bouquet with bright colors delivered tomorrow to 90210"

**Workflow**:
```
1. Orchestrator identifies multiple intents:
   - design_request (birthday, bright colors)
   - delivery_inquiry (tomorrow, 90210)
   - order_creation
   
2. Routes sequentially:
   a. Design Agent creates birthday design
   b. Inventory Agent checks availability
   c. Delivery Agent confirms delivery
   d. Order Agent prepares complete order

3. Synthesis combines all information
```

**Expected Response**:
```
I'll help you create the perfect birthday bouquet! 🎉

🎨 Design Proposal: "Birthday Celebration"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bright & Cheerful Arrangement:
• 10 Hot Pink Gerbera Daisies
• 8 Orange Roses
• 6 Yellow Sunflowers (medium)
• Purple Statice (filler)
• Bright green hypericum berries
• Rainbow ribbon bow

Size: Large (16" height)
Style: Hand-tied bouquet in clear glass vase
Includes: "Happy Birthday" banner pick

✅ Availability Check:
All flowers are in stock with excellent freshness!

🚚 Delivery Confirmation:
• ZIP Code 90210: ✓ Available
• Tomorrow Delivery: ✓ Confirmed
• Standard Window: 9 AM - 6 PM
• Delivery Fee: $12.00

💰 Complete Pricing:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flowers & Design:      $78.00
Clear Glass Vase:      $12.00
Birthday Pick:          $3.00
Delivery (90210):      $12.00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subtotal:             $105.00
Tax (8%):               $8.40
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total:                $113.40

To complete this order, I'll need:
1. Delivery address in 90210
2. Recipient name
3. Your contact information
4. Any special message for the card (free!)
5. Preferred delivery time window (optional)

Ready to place this order?
```

---

### Use Case 6.2: Wedding Consultation (Ultra Complex)

**Query**: "I'm planning a wedding for 100 guests and need centerpieces, bridal bouquet, and 5 bridesmaid bouquets in blush and gold theme"

**Workflow**:
```
1. Orchestrator recognizes: Complex multi-agent scenario
   - design_request (multiple items)
   - inventory_check (bulk flowers)
   - order_creation (large order)
   
2. Routes to multiple agents in coordination:
   - Design Agent: Creates cohesive wedding designs
   - Inventory Agent: Checks bulk availability
   - Order Agent: Calculates bulk pricing
   - Optional: Analytics Agent for timeline recommendations

3. Synthesis creates comprehensive wedding package proposal
```

**Expected Response**:
```
Congratulations on your upcoming wedding! 💍
I'll help you create a beautiful blush & gold wedding package.

🌸 Complete Wedding Flower Package
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THEME: Blush & Gold Romance
GUEST COUNT: 100
TABLES: Assuming 10-12 tables

1. BRIDAL BOUQUET
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • Blush garden roses (12 stems)
   • Champagne spray roses (15 stems)
   • White ranunculus (8 stems)
   • Gold-painted eucalyptus
   • Blush silk ribbon
   • Gold pearl pins
   Size: Large cascade style
   Price: $225

2. BRIDESMAID BOUQUETS (×5)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • Blush roses (8 stems each)
   • Champagne spray roses (10 stems each)
   • White wax flower (filler)
   • Eucalyptus greenery
   • Matching ribbon
   Size: Medium round bouquets
   Price: $95 each | Total: $475

3. CENTERPIECES (×12)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Option A - Low Centerpieces (8):
   • Blush roses and peonies
   • Gold-accented vessels
   • Soft greenery
   • Floating candles
   Price: $85 each | Subtotal: $680
   
   Option B - Tall Statement Pieces (4):
   • Dramatic height (24")
   • Cascading blush flowers
   • Gold candelabra bases
   • More elaborate design
   Price: $165 each | Subtotal: $660

   Centerpiece Total: $1,340

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PACKAGE SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bridal Bouquet:           $225.00
Bridesmaid Bouquets:      $475.00
Centerpieces:           $1,340.00
                        ─────────
Subtotal:               $2,040.00

Recommended Add-ons:
• Boutonnieres (×6):      $90.00
• Corsages (×4):          $80.00  
• Ceremony Arrangements:  $450.00
• Cake Flowers:           $75.00
                        ─────────
Complete Package:       $2,735.00

Wedding Discount: -$275.00 (10% on packages over $2,500)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL TOTAL:            $2,460.00

✅ AVAILABILITY CHECK:
All flowers available for your wedding date!
Recommended order date: 4 weeks in advance
Trial bouquet available: $75 (credited to final order)

📅 TIMELINE RECOMMENDATIONS:
• 4-6 months before: Book consultation & pay deposit
• 2 months before: Finalize design & confirm count
• 1 month before: Final payment & delivery details
• 1 week before: Final guest count confirmation
• Wedding day: Delivery 2-4 hours before ceremony

💡 INCLUDED SERVICES:
✓ Complimentary consultation
✓ Design mockups
✓ Delivery & setup
✓ Breakdown service
✓ Emergency contact day-of
✓ Backup flowers (10% extra for emergencies)

Would you like to:
1. Schedule a consultation appointment?
2. Adjust the design or quantity?
3. See alternative color schemes?
4. Book this package with a deposit?
```

---

## Error Handling Scenarios

### Use Case 7.1: Unclear Query

**Query**: "Flowers"

**Workflow**:
```
1. Orchestrator classifies: ambiguous (low confidence: 0.3)
2. Routes to: Customer Service Agent (fallback)
3. Agent requests clarification
```

**Expected Response**:
```
I'd be happy to help with flowers! To assist you better, could you tell me:

What would you like to know about flowers?

Some things I can help with:
• Check flower availability ("Do you have roses?")
• Place an order ("I want to order...")
• Track an order ("Where is order #...")
• Get care instructions ("How do I care for...")
• Design recommendations ("Suggest flowers for...")
• Delivery information ("Can you deliver to...")

What can I help you with today?
```

---

### Use Case 7.2: Out of Stock Item

**Query**: "I want to order 100 blue orchids"

**Workflow**:
```
1. Orchestrator classifies: order_creation
2. Routes to: Order Agent
3. Order Agent checks with Inventory Agent
4. Inventory returns: insufficient stock
5. Agents collaborate on alternatives
```

**Expected Response**:
```
I checked our inventory for blue orchids:

❌ Current Stock Status:
We currently have only 15 blue orchid stems available,
but you requested 100 stems.

However, I have some great alternatives:

✅ Option 1: Partial Order + Restock
• Order 15 blue orchids now
• We can order 85 more (arrives in 4 days)
• Price: $8.50/stem

✅ Option 2: Similar Flowers
• Purple dendrobium orchids (120 available)
• Blue delphinium (similar color, 200+ available)
• Blue hydrangeas (80 available)

✅ Option 3: Mixed Blue Arrangement
• Combine available blue flowers
• Create a stunning multi-variety arrangement
• Use all 15 blue orchids + complementary blues

💡 Recommendation:
For an order of this size, I'd suggest:
1. Reserve all 15 blue orchids we have
2. Special order 85 more (4-day lead time)
3. Or explore our beautiful purple orchid alternatives

What works best for your timeline?
```

---

### Use Case 7.3: Past Delivery Window

**Query**: "I need flowers delivered today at 10am"

**Current Time**: 11:30 AM

**Workflow**:
```
1. Orchestrator classifies: delivery_inquiry
2. Routes to: Delivery Agent
3. Agent detects impossible timing
4. Suggests alternatives
```

**Expected Response**:
```
I understand you need flowers urgently! However, the requested 
10:00 AM delivery time has already passed (current time: 11:30 AM).

Here's what I can offer:

⚡ Same-Day Alternatives:

Option 1: Immediate Rush Delivery
• Available: Next 2-3 hours (by 2:30 PM)
• Fee: $35.00
• Choose from ready-made arrangements

Option 2: Afternoon Delivery
• Time Window: 3:00 PM - 5:00 PM
• Fee: $25.00  
• Any custom arrangement available

Option 3: End of Day
• Time Window: 5:00 PM - 7:00 PM
• Fee: $15.00
• Full customization available

All options include:
✓ Real-time tracking
✓ SMS notifications
✓ Direct contact with driver

Would any of these work for you? Or if tomorrow works better,
we can schedule a specific morning time window!
```

---

### Use Case 7.4: Invalid Order Number

**Query**: "What's the status of order #99999?"

**Workflow**:
```
1. Orchestrator classifies: order_tracking
2. Routes to: Order Agent
3. Agent searches for order
4. Order not found
5. Agent requests clarification
```

**Expected Response**:
```
I couldn't find order #99999 in our system.

Let me help you locate your order:

❓ Common Issues:
• Order number might be mistyped
• Order might be under a different number
• Order might not be confirmed yet

🔍 Ways to Find Your Order:

1. Check your email confirmation
   • Subject: "Bloomer Order Confirmation"
   • Order # is at the top

2. Search by phone number
   • What phone number was used for the order?

3. Search by date
   • When was the order placed?

4. Recent orders
   • Show me your recent orders on this account

Or, if you haven't placed an order yet, I can help you create one!

How would you like to proceed?
```

---

## Pro Tips for Users

### Getting the Best Results

1. **Be Specific**: "2 dozen red roses" vs "some flowers"
2. **Include Context**: "For a wedding" helps agents make better suggestions
3. **Mention Timeline**: "Need by tomorrow" ensures proper routing
4. **Ask Follow-ups**: Conversations can continue naturally
5. **Request Alternatives**: "What else do you suggest?" expands options

### Example of Good vs Vague Queries

❌ Vague: "Flowers for mom"
✅ Better: "Birthday flowers for my mom who likes pink and purple"

❌ Vague: "Can you deliver?"
✅ Better: "Can you deliver to 90210 tomorrow afternoon?"

❌ Vague: "How much?"
✅ Better: "How much for 2 dozen roses with delivery?"

---

These use cases demonstrate how Bloomer Agent handles everything from simple queries to complex multi-agent workflows, always maintaining a helpful, professional, and personalized experience for flower shop operations.

