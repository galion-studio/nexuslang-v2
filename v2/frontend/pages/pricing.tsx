// Pricing Page for developer.galion.app
import Head from 'next/head'

export default function PricingPage() {
  const tiers = [
    {
      name: 'Free',
      price: 0,
      credits: 100,
      features: ['100 credits/month', 'Basic AI models', 'Community support', '3 projects max']
    },
    {
      name: 'Creator',
      price: 20,
      credits: 1000,
      features: ['1,000 credits/month', 'All AI models', 'Priority support', '10 projects', 'Commercial license']
    },
    {
      name: 'Professional',
      price: 50,
      credits: 5000,
      features: ['5,000 credits/month', 'Team features (5 members)', '50 projects', 'Advanced analytics']
    },
    {
      name: 'Business',
      price: 200,
      credits: 25000,
      features: ['25,000 credits/month', 'Team (20 members)', '200 projects', 'White-label', 'Custom integrations']
    }
  ]

  return (
    <div style={{padding: '50px'}}>
      <Head>
        <title>Pricing - developer.galion.app</title>
      </Head>

      <h1 style={{textAlign: 'center'}}>Simple, Transparent Pricing</h1>
      <p style={{textAlign: 'center', color: '#666'}}>Choose the plan that's right for you</p>

      <div style={{
        marginTop: '50px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '30px',
        maxWidth: '1200px',
        margin: '50px auto'
      }}>
        {tiers.map(tier => (
          <div key={tier.name} style={{
            padding: '30px',
            backgroundColor: 'white',
            border: '2px solid #e5e7eb',
            borderRadius: '16px',
            textAlign: 'center'
          }}>
            <h2>{tier.name}</h2>
            <div style={{fontSize: '48px', fontWeight: 'bold', margin: '20px 0'}}>
              ${tier.price}
              <span style={{fontSize: '16px', fontWeight: 'normal', color: '#666'}}>/month</span>
            </div>
            <p style={{color: '#666'}}>{tier.credits.toLocaleString()} credits/month</p>
            
            <ul style={{textAlign: 'left', marginTop: '30px', paddingLeft: '20px'}}>
              {tier.features.map(feature => (
                <li key={feature} style={{marginBottom: '10px'}}>{feature}</li>
              ))}
            </ul>
            
            <button style={{
              marginTop: '30px',
              padding: '12px 32px',
              backgroundColor: '#6366f1',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              cursor: 'pointer',
              width: '100%'
            }}>
              {tier.price === 0 ? 'Get Started' : 'Subscribe'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

