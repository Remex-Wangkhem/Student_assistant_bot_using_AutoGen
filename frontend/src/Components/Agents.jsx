import { Box, Button, Flex, VStack } from '@chakra-ui/react';

const Agents = ({ onSelectAgent }) => {
    const handleClick = (message) => {
        onSelectAgent(message);
    };

    return (
        <Flex flexDirection="column" marginLeft={2} height="full">
            {[ 
                { name: 'Agent 1', message: 'Hi, I am Agent 1' },
                { name: 'Agent 2', message: 'Hi, I am Agent 2' },
                { name: 'Chat Manager', message: 'Hi, I am Chat Manager' },
            ].map((agent, index) => (
                <Box
                    key={index}
                    w="20rem"
                    p="4"
                    bg="gray.200"
                    borderLeftWidth="1px"
                    h="13rem"
                    marginTop={index > 0 ? 2 : 0}
                >
                    <VStack spacing="4" align="stretch">
                        <Button colorScheme="teal" onClick={() => handleClick(agent.message)}>
                            {agent.name}
                        </Button>
                    </VStack>
                </Box>
            ))}
        </Flex>
    );
};

export default Agents;

// import { Box, Button, Flex, VStack } from '@chakra-ui/react';

// const Agents = ({ onSelectAgent }) => {
//     const handleClick = (message) => {
//         onSelectAgent(message);
//     };

//     return (
//         <Flex flexDirection='column' marginLeft={2} h="full">
//         <Box
//             w="20rem"
//             p="4"
//             bg="gray.200"
//             borderLeftWidth="1px"
//             h="13rem"
//         >
//             <VStack spacing="4" align="stretch">
//                 <Button colorScheme="teal" onClick={() => handleClick('Hi, I am Agent 1')}>Agent 1</Button>
//             </VStack>
//         </Box>
//                 <Box
//                 w="20rem"
//                 p="4"
//                 bg="gray.200"
//                 borderLeftWidth="1px"
//                 h="13rem"
//                 marginTop={2}
//             >
//                 <VStack spacing="4" align="stretch">
//                     <Button colorScheme="teal" onClick={() => handleClick('Hi, I am Agent 2')}>Agent 2</Button>
//                 </VStack>
//             </Box>
//                     <Box
//                     w="20rem"
//                     p="4"
//                     bg="gray.200"
//                     borderLeftWidth="1px"
//                     h="13rem"
//                     marginTop={2}
//                 >
//                     <VStack spacing="4" align="stretch">
//                         <Button colorScheme="teal" onClick={() => handleClick('Hi, I am Chat Manager')}>Chat Manager</Button>
//                     </VStack>
//                 </Box>
//                 </Flex>
//     );
// };

// export default Agents;

