import { motion } from "framer-motion";

export default function StatsCard({
    title,
    value,
    icon: Icon,
    color="#8b5cf6",
    change="+0%",
    changeColor="#22c55e"
}){

    return(

        <motion.div
            className="stats-card"
            initial={{opacity:0,y:20}}
            animate={{opacity:1,y:0}}
            transition={{duration:.35}}
            whileHover={{
                y:-6,
                scale:1.02
            }}
        >

            <div className="stats-header">

                <div
                    className="stats-icon"
                    style={{background:color}}
                >

                    <Icon size={20}/>

                </div>

                <span className="stats-title">

                    {title}

                </span>

            </div>

            <h2 className="stats-value">

                {value}

            </h2>

            <div className="stats-footer">

                <span
                    className="stats-change"
                    style={{color:changeColor}}
                >

                    {change}

                </span>

                <span className="stats-period">

                    vs last 7 days

                </span>

            </div>

        </motion.div>

    )

}
