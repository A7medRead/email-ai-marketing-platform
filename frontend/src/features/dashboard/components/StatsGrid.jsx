import {
    Mail,
    MousePointerClick,
    ShieldCheck,
    AlertTriangle,
    UserMinus,
    Send
} from "lucide-react";

import StatsCard from "./StatsCard";

export default function StatsGrid({stats,marketing}){

    const openRate = stats.total_sent
        ? ((marketing.opened / stats.total_sent) * 100).toFixed(1)
        : 0;

    const clickRate = stats.total_sent
        ? ((marketing.clicked / stats.total_sent) * 100).toFixed(1)
        : 0;

    const deliveryRate = stats.total_sent
        ? (
            ((stats.total_sent - stats.total_failed) /
            stats.total_sent) * 100
        ).toFixed(1)
        : 0;

    const bounceRate = stats.total_sent
        ? (
            (stats.total_failed /
            stats.total_sent) * 100
        ).toFixed(1)
        : 0;

    const unsubscribeRate = "0.4";

    const cards=[

        {
            title:"Emails Sent",
            value:stats.total_sent,
            icon:Send,
            color:"#7c3aed",
            change:"+12.4%"
        },

        {
            title:"Open Rate",
            value:`${openRate}%`,
            icon:Mail,
            color:"#10b981",
            change:"+8.7%"
        },

        {
            title:"Click Rate",
            value:`${clickRate}%`,
            icon:MousePointerClick,
            color:"#2563eb",
            change:"+3.1%"
        },

        {
            title:"Delivery Rate",
            value:`${deliveryRate}%`,
            icon:ShieldCheck,
            color:"#f97316",
            change:"+0.6%"
        },

        {
            title:"Bounce Rate",
            value:`${bounceRate}%`,
            icon:AlertTriangle,
            color:"#ef4444",
            change:"-0.1%",
            changeColor:"#ef4444"
        },

        {
            title:"Unsubscribe Rate",
            value:`${unsubscribeRate}%`,
            icon:UserMinus,
            color:"#8b5cf6",
            change:"-0.2%",
            changeColor:"#ef4444"
        }

    ];

    return(

        <div className="stats-grid">

            {

                cards.map(card=>(

                    <StatsCard
                        key={card.title}
                        {...card}
                    />

                ))

            }

        </div>

    )

}
